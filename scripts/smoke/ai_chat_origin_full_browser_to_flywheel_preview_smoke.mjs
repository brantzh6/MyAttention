import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const { chromium } = require('../../services/web/node_modules/playwright-core')

const BASE_URL = (process.env.BASE_URL || 'http://127.0.0.1:3002').replace(/\/+$/, '')
const API_URL = (process.env.API_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')
const SHORT_TIMEOUT_MS = 15000
const LONG_TIMEOUT_MS = 60000
const CHAT_RESPONSE_TIMEOUT_MS = 120000

const TEST_MESSAGE = 'Please suggest one small improvement for the IKE flywheel inspection loop that would make the candidate extraction more useful. Keep it inspect-only: no automatic execution, no promotion, and controller review required.'

function makeCheckState() {
  return {
    chat_page_loaded: false,
    chat_input_found: false,
    message_submitted: false,
    assistant_response_received: false,
    response_has_content: false,
    response_no_error: false,
    handoff_button_found: false,
    handoff_navigation_successful: false,
    evolution_page_loaded: false,
    handoff_material_visible: false,
    chat_origin_guided_path_visible: false,
    inspect_button_found: false,
    inspect_button_enabled: false,
    inspect_endpoint_called: false,
    inspect_has_candidates: false,
    inspect_has_knowledge_candidates: false,
    inspect_has_evolution_candidates: false,
    inspect_truth_boundary_visible: false,
    candidates_section_visible: false,
    candidate_checkbox_found: false,
    candidate_selected: false,
    preview_button_found: false,
    preview_button_enabled: false,
    preview_endpoint_called: false,
    candidate_packet_non_null: false,
    handoff_preview_non_null: false,
    candidate_packet_ui_visible: false,
    handoff_preview_ui_visible: false,
    truth_boundary_visible: false,
    truth_boundary_inspect_only: false,
    truth_boundary_non_canonical: false,
    truth_boundary_no_auto_execution: false,
    no_worker_execution: false,
    no_persistence: false,
    no_promotion: false,
    console_errors_clean: true,
    network_errors_clean: true,
  }
}

async function run() {
  const checks = makeCheckState()
  const evidence = {
    browser_steps: [],
    api_calls: [],
    console_errors: [],
    network_errors: [],
    inspect_result: null,
    preview_result: null,
    screenshots: [],
    timestamps: {},
  }
  const errors = []
  let browser

  try {
    browser = await chromium.launch({ headless: true })
    const context = await browser.newContext({
      permissions: ['clipboard-read', 'clipboard-write'],
    })
    const page = await context.newPage()

    page.setDefaultTimeout(SHORT_TIMEOUT_MS)
    page.setDefaultNavigationTimeout(LONG_TIMEOUT_MS)

    // Capture console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        evidence.console_errors.push(msg.text())
        checks.console_errors_clean = false
      }
    })

    // Capture network errors
    page.on('requestfailed', (request) => {
      evidence.network_errors.push({
        url: request.url(),
        failure: request.failure()?.errorText || 'unknown',
      })
      checks.network_errors_clean = false
    })

    // Capture API calls (requests + responses). This avoids false negatives when
    // a POST is sent but the response has not arrived before the smoke exits.
    page.on('request', (request) => {
      const url = request.url()
      if (url.includes('/api/') && !url.includes('/_next/')) {
        evidence.api_calls.push({
          url,
          method: request.method(),
          status: 'pending',
        })
      }
    })

    page.on('response', async (response) => {
      const url = response.url()
      if (url.includes('/api/') && !url.includes('/_next/')) {
        const call = {
          url,
          method: response.request().method(),
          status: response.status(),
        }
        // Capture inspect and preview responses
        if (url.includes('/flywheel/inspect') && response.request().method() === 'POST') {
          try {
            const body = await response.json()
            evidence.inspect_result = body
            call.body_preview = JSON.stringify(body).substring(0, 500)
          } catch {}
        }
        if (url.includes('/flywheel/task-packet/preview') && response.request().method() === 'POST') {
          try {
            const body = await response.json()
            evidence.preview_result = body
            call.body_preview = JSON.stringify(body).substring(0, 500)
          } catch {}
        }
        evidence.api_calls.push(call)
      }
    })

    // Step 1: Navigate to /chat
    evidence.browser_steps.push('Step 1: Navigate to /chat')
    evidence.timestamps.start = new Date().toISOString()
    await page.goto(`${BASE_URL}/chat`, { waitUntil: 'domcontentloaded' })
    checks.chat_page_loaded = true
    evidence.browser_steps.push('Chat page loaded successfully')

    // Take screenshot
    const screenshot1 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_01_chat_page.png' })
    evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_01_chat_page.png')

    // Step 2: Find and fill chat input
    evidence.browser_steps.push('Step 2: Find chat input')
    const inputSelector = "input[type='text'][placeholder], textarea[placeholder]"
    const inputElement = await page.waitForSelector(inputSelector, { timeout: SHORT_TIMEOUT_MS })
    checks.chat_input_found = true
    evidence.browser_steps.push('Chat input found')

    // Fill and submit message
    await inputElement.fill(TEST_MESSAGE)
    evidence.browser_steps.push('Message entered')

    const screenshot2 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_02_message_entered.png' })
    evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_02_message_entered.png')

    // Submit the message
    const submitButton = await page.waitForSelector("button[type='submit']", { timeout: SHORT_TIMEOUT_MS })
    await submitButton.click()
    checks.message_submitted = true
    evidence.timestamps.submit = new Date().toISOString()
    evidence.browser_steps.push('Message submitted')

    const screenshot3 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_03_message_submitted.png' })
    evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_03_message_submitted.png')

    // Step 3: Wait for assistant response
    evidence.browser_steps.push('Step 3: Wait for assistant response')
    // Wait for loading spinner to disappear (isLoading state ends)
    const loadingSpinner = page.locator('.animate-spin').last()
    try {
      await loadingSpinner.waitFor({ state: 'hidden', timeout: CHAT_RESPONSE_TIMEOUT_MS })
    } catch {
      // If spinner not found, try waiting for response content directly
      evidence.browser_steps.push('Spinner wait timeout, checking for content')
    }

    // Wait for assistant message div (justify-start class for assistant messages)
    const assistantMessageDiv = page.locator('div.justify-start').filter({ has: page.locator('div.bg-muted, div.bg-white') })
    await assistantMessageDiv.waitFor({ timeout: SHORT_TIMEOUT_MS })

    // Additional wait for content to settle
    await page.waitForTimeout(3000)

    checks.assistant_response_received = true
    evidence.timestamps.response = new Date().toISOString()
    evidence.browser_steps.push('Assistant response received')

    const screenshot4 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_04_response_received.png' })
    evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_04_response_received.png')

    // Check response content
    const bodyText = await page.locator('body').innerText()
    checks.response_has_content = bodyText.length > 100 && !bodyText.includes('error')
    checks.response_no_error = !bodyText.toLowerCase().includes('error') && !bodyText.toLowerCase().includes('failed')
    evidence.browser_steps.push(`Response content check: has_content=${checks.response_has_content}, no_error=${checks.response_no_error}`)

    // Step 4: Find handoff button and navigate to evolution
    evidence.browser_steps.push('Step 4: Find handoff control')

    // Look for the flywheel handoff button - it has MessageSquare icon and text
    // The button is at the bottom of assistant messages with text "进入飞轮" (zh-CN) or "Open in Flywheel" (en)
    const handoffButtonSelectors = [
      "button:has-text('飞轮')",
      "button:has-text('Flywheel')",
      "button:has(svg.lucide-message-square)",
      "button:has(svg[class*='lucide-message-square'])",
    ]

    let handoffButton = null
    for (const selector of handoffButtonSelectors) {
      try {
        const count = await page.locator(selector).count()
        if (count > 0) {
          // Find a visible and enabled button with this selector
          for (let i = 0; i < count; i++) {
            const btn = page.locator(selector).nth(i)
            if (await btn.isVisible() && await btn.isEnabled()) {
              handoffButton = btn
              checks.handoff_button_found = true
              evidence.browser_steps.push(`Handoff button found with selector: ${selector}`)
              break
            }
          }
          if (checks.handoff_button_found) break
        }
      } catch {}
    }

    // If not found by selectors, search for button near assistant response content
    if (!checks.handoff_button_found) {
      evidence.browser_steps.push('Handoff button not found with primary selectors, searching broader')
      try {
        // Look for buttons in the assistant message area
        const assistantArea = page.locator('div.justify-start').last()
        const buttonsInAssistant = await assistantArea.locator('button').all()
        for (const btn of buttonsInAssistant) {
          if (await btn.isVisible() && await btn.isEnabled()) {
            const buttonText = await btn.innerText() || ''
            if (buttonText.includes('飞轮') || buttonText.includes('Flywheel') || buttonText.includes('MessageSquare')) {
              handoffButton = btn
              checks.handoff_button_found = true
              evidence.browser_steps.push(`Handoff button found via area search: ${buttonText}`)
              break
            }
          }
        }
      } catch {}
    }

    if (checks.handoff_button_found && handoffButton) {
      const screenshot5 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_05_handoff_button_found.png' })
      evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_05_handoff_button_found.png')

      await handoffButton.click()
      evidence.timestamps.handoff_click = new Date().toISOString()
      evidence.browser_steps.push('Handoff button clicked')

      // Wait for navigation to /evolution?handoff=chat
      await page.waitForURL(/\/evolution/, { timeout: LONG_TIMEOUT_MS })
      checks.handoff_navigation_successful = true
      checks.evolution_page_loaded = true
      evidence.browser_steps.push('Navigated to /evolution')

      // Step 5: Wait for actual handoff state before proceeding
      // CRITICAL: Must wait for React state to populate from sessionStorage before Run Inspect
      // The handoff click stores payload in sessionStorage, then useEffect reads it on mount
      evidence.browser_steps.push('Step 5: Wait for actual handoff state')

      let handoffStateReady = false
      let handoffWaitOutcome = 'unknown'
      const handoffWaitStart = Date.now()

      // Primary: wait for handoff notice text indicating React state populated
      try {
        await page.getByText('Imported transient chat input', { exact: false }).waitFor({ timeout: SHORT_TIMEOUT_MS })
        handoffWaitOutcome = 'success: handoff_notice_text_appeared'
        handoffStateReady = true
        evidence.browser_steps.push(`[${Date.now() - handoffWaitStart}ms] Handoff notice text appeared - React state populated`)
        evidence.timestamps.handoff_state_ready = new Date().toISOString()
      } catch (e) {
        handoffWaitOutcome = `failed: timeout_after_${SHORT_TIMEOUT_MS}ms`
        evidence.browser_steps.push(`[${Date.now() - handoffWaitStart}ms] Handoff notice did not appear within timeout - state may not be populated`)
        evidence.browser_steps.push(`Wait error: ${e?.message || 'timeout'}`)
      }

      // Secondary: check for chat-origin guided path visible (alternative indicator)
      if (!handoffStateReady) {
        try {
          const guidedPathText = await page.locator('text=/Chat-origin|FlywheelGuidedPath/').first().textContent({ timeout: 5000 })
          if (guidedPathText && guidedPathText.length > 0) {
            handoffWaitOutcome = 'success: guided_path_visible'
            handoffStateReady = true
            evidence.browser_steps.push('Guided path visible - handoff state confirmed via alternative indicator')
          }
        } catch {
          evidence.browser_steps.push('Guided path not found as fallback')
        }
      }

      // Tertiary: verify textarea has real handoff content (not placeholder)
      // CRITICAL: Wait for textarea to have actual content, not just appear in DOM
      // This ensures reducer state is populated before clicking Run Inspect
      const textareaLocator = page.locator('textarea').first()
      try {
        // Wait for textarea to have content (inputValue reflects React state for controlled components)
        await page.waitForFunction(
          () => {
            const textarea = document.querySelector('textarea')
            if (!textarea) return false
            const value = textarea.value || ''
            return value.length > 50 && (value.includes('User:') || value.includes('Assistant:'))
          },
          { timeout: 5000 }
        )
        const textareaValue = await textareaLocator.inputValue({ timeout: 5000 })
        evidence.browser_steps.push(`Textarea has real content (${textareaValue.length} chars) - handoff material loaded`)
        if (!handoffStateReady) {
          handoffWaitOutcome = 'success: textarea_has_real_content'
          handoffStateReady = true
        }
      } catch (e) {
        const textareaValue = await textareaLocator.inputValue({ timeout: 1000 }).catch(() => '')
        evidence.browser_steps.push(`Textarea content check failed or insufficient (${textareaValue.length} chars): ${e?.message || 'timeout'}`)
      }

      evidence.browser_steps.push(`Handoff state ready: ${handoffStateReady} (outcome: ${handoffWaitOutcome})`)
      checks.handoff_material_visible = handoffStateReady

      // Check for chat-origin guided path - key indicator that handoff was processed
      // NOTE: `innerText()` can be a false negative if React is still rendering the handoff UI.
      // Prefer waiting for the explicit guided-path header to become visible.
      let guidedPathVisible = false
      try {
        await page
          .locator('h4:has-text("Chat-origin Flywheel Path")')
          .first()
          .waitFor({ state: 'visible', timeout: 5000 })
        guidedPathVisible = true
      } catch (e) {
        guidedPathVisible = false
      }

      if (!guidedPathVisible) {
        // Fallback: scan visible body text for older/alternate markers (kept to avoid regressing real signal loss).
        const evolutionBodyText = await page.locator('body').innerText()
        guidedPathVisible =
          evolutionBodyText.includes('Chat-origin Flywheel Path') ||
          evolutionBodyText.includes('Chat-origin') ||
          evolutionBodyText.includes('FlywheelGuidedPath')
      }

      checks.chat_origin_guided_path_visible = guidedPathVisible
      evidence.browser_steps.push(`Guided path visible: ${checks.chat_origin_guided_path_visible}`)

      const screenshot6 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_06_evolution_page.png' })
      evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_06_evolution_page.png')
    } else {
      evidence.browser_steps.push('Handoff button not found - attempting direct navigation')
      await page.goto(`${BASE_URL}/evolution?handoff=chat`, { waitUntil: 'domcontentloaded' })
      checks.evolution_page_loaded = true
      evidence.browser_steps.push('Direct navigation to /evolution?handoff=chat successful')

      // Direct navigation without prior sessionStorage set will likely fail handoff load
      // Record this as handoff state not ready
      checks.handoff_material_visible = false
      checks.chat_origin_guided_path_visible = false
      evidence.browser_steps.push('Direct navigation: handoff state not ready (no sessionStorage payload from chat flow)')

      await page.waitForTimeout(2000)

      const screenshot6 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_06_evolution_direct.png' })
      evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_06_evolution_direct.png')
    }

    // Pre-Run Inspect assertion: verify handoff material is actually present
    // Do not proceed with Run Inspect if handoff state is not confirmed
    const screenshot7 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_07_handoff_context.png' })
    evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_07_handoff_context.png')

    // Step 6: Run inspect
    evidence.browser_steps.push('Step 6: Run inspect')

    // CRITICAL: Assert handoff state is ready before looking for Run Inspect button
    if (!checks.handoff_material_visible && !checks.chat_origin_guided_path_visible) {
      evidence.browser_steps.push('BLOCKER: Handoff state not ready - skipping Run Inspect to avoid false failure')
      evidence.browser_steps.push('This indicates sessionStorage handoff payload was not properly propagated or React state did not populate')
      checks.inspect_endpoint_called = false
      // Do not attempt Run Inspect if handoff material is not confirmed present
    } else {
      // Handoff state confirmed - proceed with Run Inspect
      evidence.browser_steps.push('Handoff state confirmed - proceeding with Run Inspect')

      // Prefer the exact Run Inspect control; a generic "Inspect" match can
      // select the execution feedback inspect button and produce a false
      // negative (no /flywheel/inspect request) for the mainline smoke.
      const inspectButtonSelectors = [
        "button:has-text('提交探测')",
        "button:has-text('Run Inspect')",
        "button[data-testid*='run-inspect']",
        "button[data-testid*='inspect']",
        "button[aria-label*='run inspect']",
        "button[aria-label*='inspect']",
        "button:has-text('Inspect')",
      ]

      let inspectButton = null
      for (const selector of inspectButtonSelectors) {
        try {
          const count = await page.locator(selector).count()
          if (count > 0) {
            inspectButton = page.locator(selector).first()
            if (await inspectButton.isVisible() && await inspectButton.isEnabled()) {
              checks.inspect_button_found = true
              checks.inspect_button_enabled = true
              evidence.browser_steps.push(`Inspect button found with selector: ${selector}`)
              break
            }
          }
        } catch {}
      }

      if (checks.inspect_button_found && inspectButton) {
        await inspectButton.click()
        evidence.timestamps.inspect_click = new Date().toISOString()
        evidence.browser_steps.push('Inspect button clicked')

      // Wait for inspect response (avoid false negatives on slower runtimes).
      try {
        await page.waitForResponse(
          (resp) =>
            resp.url().includes('/api/conversation-runtime/flywheel/inspect') &&
            resp.request().method() === 'POST',
          { timeout: 60000 },
        )
      } catch {
        // If the runtime is slow or stalled, we still record whether the request was issued.
      }

      // Check if inspect endpoint was called
      const inspectCall = evidence.api_calls.find(c => c.url.includes('/flywheel/inspect') && c.method === 'POST')
      checks.inspect_endpoint_called = !!inspectCall
      evidence.browser_steps.push(`Inspect endpoint called: ${checks.inspect_endpoint_called} (status: ${inspectCall?.status || 'N/A'})`)

      const screenshot8 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_08_after_inspect.png' })
      evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_08_after_inspect.png')

      // Check inspect result structure
      if (evidence.inspect_result) {
        checks.inspect_has_candidates =
          (evidence.inspect_result.knowledge_delta_candidates?.length > 0) ||
          (evidence.inspect_result.evolution_trigger_candidates?.length > 0) ||
          (evidence.inspect_result.source_candidates?.length > 0)
        checks.inspect_has_knowledge_candidates = evidence.inspect_result.knowledge_delta_candidates?.length > 0
        checks.inspect_has_evolution_candidates = evidence.inspect_result.evolution_trigger_candidates?.length > 0

        const truthBoundary = evidence.inspect_result.truth_boundary || []
        checks.inspect_truth_boundary_visible = truthBoundary.length > 0

        evidence.browser_steps.push(`Inspect result: knowledge_candidates=${evidence.inspect_result.knowledge_delta_candidates?.length || 0}, evolution_candidates=${evidence.inspect_result.evolution_trigger_candidates?.length || 0}`)
      }

      // Check for candidates in UI
      const afterInspectText = await page.locator('body').innerText()
      checks.candidates_section_visible =
        afterInspectText.includes('Candidate') ||
        afterInspectText.includes('knowledge') ||
        afterInspectText.includes('evolution') ||
        afterInspectText.includes('Selection')

      evidence.browser_steps.push(`Candidates section visible: ${checks.candidates_section_visible}`)
      } else {
        evidence.browser_steps.push('Inspect button not found')
      }

      // Step 7: Select candidates
      evidence.browser_steps.push('Step 7: Select candidates')

      const checkboxes = await page.locator('input[type="checkbox"]').all()
      checks.candidate_checkbox_found = checkboxes.length > 0
      evidence.browser_steps.push(`Checkbox count: ${checkboxes.length}`)

      if (checkboxes.length > 0) {
        // Select all visible candidate checkboxes so mixed knowledge/evolution
        // previews exercise candidate_packet and handoff_preview generation.
        for (let i = 0; i < checkboxes.length; i++) {
          try {
            const checkbox = checkboxes[i]
            if (await checkbox.isVisible() && await checkbox.isEnabled()) {
              await checkbox.check()
              evidence.browser_steps.push(`Selected checkbox ${i + 1}`)
            }
          } catch {}
        }

        // Verify selection
        const checkedCount = await page.locator('input[type="checkbox"]:checked').count()
        checks.candidate_selected = checkedCount > 0
        evidence.browser_steps.push(`Candidates selected: ${checkedCount}`)

        const screenshot9 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_09_candidates_selected.png' })
        evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_09_candidates_selected.png')
      }

      // Step 8: Request preview
      evidence.browser_steps.push('Step 8: Request preview')

      const previewButtonSelectors = [
        "button:has-text('Preview')",
        "button:has-text('Request Preview')",
        "button[data-testid*='preview']",
      ]

      let previewButton = null
      for (const selector of previewButtonSelectors) {
        try {
          const count = await page.locator(selector).count()
          if (count > 0) {
            previewButton = page.locator(selector).first()
            if (await previewButton.isVisible()) {
              checks.preview_button_found = true
              checks.preview_button_enabled = await previewButton.isEnabled()
              evidence.browser_steps.push(`Preview button found: enabled=${checks.preview_button_enabled}`)
              break
            }
          }
        } catch {}
      }

      if (checks.preview_button_found && checks.preview_button_enabled && previewButton) {
        await previewButton.click()
        evidence.timestamps.preview_click = new Date().toISOString()
        evidence.browser_steps.push('Preview button clicked')

        // Wait for preview result
        await page.waitForTimeout(8000) // Allow API call to complete

        // Check if preview endpoint was called
        const previewCall = evidence.api_calls.find(c => c.url.includes('/task-packet/preview') && c.method === 'POST')
        checks.preview_endpoint_called = !!previewCall
        evidence.browser_steps.push(`Preview endpoint called: ${checks.preview_endpoint_called} (status: ${previewCall?.status || 'N/A'})`)

      const screenshot10 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_10_after_preview.png' })
      evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_10_after_preview.png')

      // Check preview result structure
      if (evidence.preview_result) {
        checks.candidate_packet_non_null = evidence.preview_result.candidate_packet != null
        checks.handoff_preview_non_null = evidence.preview_result.handoff_preview != null

        evidence.browser_steps.push(`Candidate packet non-null: ${checks.candidate_packet_non_null}`)
        evidence.browser_steps.push(`Handoff preview non-null: ${checks.handoff_preview_non_null}`)
      }

      // Check for preview in UI
      const afterPreviewText = await page.locator('body').innerText()
      checks.candidate_packet_ui_visible =
        afterPreviewText.includes('Candidate Packet') ||
        afterPreviewText.includes('candidate_packet') ||
        afterPreviewText.includes('Packet')

      checks.handoff_preview_ui_visible =
        afterPreviewText.includes('Handoff') ||
        afterPreviewText.includes('Preview') ||
        afterPreviewText.includes('delegate')

      // Check truth boundaries
      checks.truth_boundary_visible =
        afterPreviewText.includes('inspect-only') ||
        afterPreviewText.includes('Inspect-only') ||
        afterPreviewText.includes('non-canonical') ||
        afterPreviewText.includes('non_canonical')

      checks.truth_boundary_inspect_only =
        afterPreviewText.includes('inspect-only') ||
        afterPreviewText.includes('Inspect-only') ||
        afterPreviewText.includes('inspect_only')

      checks.truth_boundary_non_canonical =
        afterPreviewText.includes('non-canonical') ||
        afterPreviewText.includes('non_canonical')

      checks.truth_boundary_no_auto_execution =
        afterPreviewText.includes('no automatic') ||
        afterPreviewText.includes('No automatic') ||
        afterPreviewText.includes('does not trigger') ||
        afterPreviewText.includes('manual')

      evidence.browser_steps.push(`Candidate packet UI visible: ${checks.candidate_packet_ui_visible}`)
      evidence.browser_steps.push(`Handoff preview UI visible: ${checks.handoff_preview_ui_visible}`)
      evidence.browser_steps.push(`Truth boundary visible: ${checks.truth_boundary_visible}`)
      evidence.browser_steps.push(`Truth boundary inspect-only: ${checks.truth_boundary_inspect_only}`)
      evidence.browser_steps.push(`Truth boundary non-canonical: ${checks.truth_boundary_non_canonical}`)
      evidence.browser_steps.push(`Truth boundary no-auto-execution: ${checks.truth_boundary_no_auto_execution}`)
      } else {
        evidence.browser_steps.push('Preview button not found or not enabled')
      }

      // Step 9: Verify stop condition - no worker execution, persistence, promotion
      evidence.browser_steps.push('Step 9: Verify stop condition')
      const finalBodyText = await page.locator('body').innerText()

      checks.no_worker_execution =
        // Avoid false positives from copyable packet text (e.g., "Execution Feedback").
        !finalBodyText.includes('Worker running') &&
        !finalBodyText.includes('worker_running') &&
        !finalBodyText.includes('Executing worker') &&
        !finalBodyText.includes('executing worker')

      const explicitlyNoPersist =
        finalBodyText.includes('No data is persisted') ||
        finalBodyText.includes('No data is persisted.')

      const persistenceSignal =
        (!explicitlyNoPersist && (finalBodyText.includes('Persisted') || finalBodyText.includes('persisted'))) ||
        // "Saved to clipboard" is allowed; do not treat it as persistence.
        finalBodyText.includes('Saved to database')

      checks.no_persistence = !persistenceSignal

      checks.no_promotion =
        !finalBodyText.includes('Promoted') &&
        !finalBodyText.includes('promoted') &&
        !finalBodyText.includes('Accepted as truth')

      evidence.browser_steps.push(`No worker execution: ${checks.no_worker_execution}`)
      evidence.browser_steps.push(`No persistence: ${checks.no_persistence}`)
      evidence.browser_steps.push(`No promotion: ${checks.no_promotion}`)
    } // End of handoff-ready conditional block

    const screenshot11 = await page.screenshot({ path: '.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_11_final.png' })
    evidence.screenshots.push('.runtime/ui-probes/ai_chat_origin_full_browser_to_flywheel_preview_11_final.png')

    evidence.timestamps.end = new Date().toISOString()
    evidence.browser_steps.push('Validation complete')

  } catch (error) {
    errors.push({
      name: error?.name || 'Error',
      message: error?.message || String(error),
    })
  } finally {
    if (browser) await browser.close()
  }

  const failedChecks = Object.entries(checks)
    .filter(([, passed]) => !passed)
    .map(([name]) => name)

  // Determine recommendation
  let recommendation = 'reject'
  if (errors.length === 0 && failedChecks.length === 0) {
    recommendation = 'accept'
  } else if (errors.length === 0 &&
             checks.chat_page_loaded &&
             checks.message_submitted &&
             checks.assistant_response_received &&
             checks.evolution_page_loaded &&
             checks.inspect_endpoint_called &&
             checks.preview_endpoint_called &&
             checks.candidate_packet_non_null &&
             checks.handoff_preview_non_null &&
             checks.truth_boundary_visible) {
    recommendation = 'accept_with_changes'
  }

  return {
    ok: failedChecks.length === 0 && errors.length === 0,
    base_url: BASE_URL,
    api_url: API_URL,
    test_message: TEST_MESSAGE,
    checks,
    failed_checks: failedChecks,
    evidence,
    errors,
    recommendation,
    validation_level: 'L4_browser_ui_smoke',
    stop_before: ['worker_execution', 'persistence', 'promotion'],
  }
}

run()
  .then((summary) => {
    process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`)
    if (!summary.ok) process.exitCode = 1
  })
  .catch((error) => {
    const summary = {
      ok: false,
      base_url: BASE_URL,
      api_url: API_URL,
      test_message: TEST_MESSAGE,
      checks: makeCheckState(),
      failed_checks: ['script_error'],
      evidence: { browser_steps: [], api_calls: [], console_errors: [], network_errors: [], screenshots: [] },
      errors: [
        {
          name: error?.name || 'Error',
          message: error?.message || String(error),
        },
      ],
      recommendation: 'reject',
      validation_level: 'L4_browser_ui_smoke',
      stop_before: ['worker_execution', 'persistence', 'promotion'],
    }
    process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`)
    process.exitCode = 1
  })
