import fs from 'node:fs'
import path from 'node:path'
import process from 'node:process'

import { chromium } from 'playwright-core'

function parseArgs(argv) {
  const args = { url: '', expect: '', screenshotDir: '' }
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i]
    if (token === '--url') args.url = argv[i + 1] || ''
    if (token === '--expect') args.expect = argv[i + 1] || ''
    if (token === '--screenshot-dir') args.screenshotDir = argv[i + 1] || ''
  }
  return args
}

function resolveChromePath() {
  const envCandidates = [
    process.env.PLAYWRIGHT_CHROME_PATH,
    process.env.CHROME_PATH,
    process.env.GOOGLE_CHROME_BIN,
  ].filter(Boolean)

  const platform = process.platform
  const commonCandidates = {
    win32: [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
      'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    ],
    darwin: [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    ],
    linux: [
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
      '/snap/bin/chromium',
      '/usr/bin/microsoft-edge',
    ],
  }

  const candidates = [...envCandidates, ...(commonCandidates[platform] || [])]
  return candidates.find((candidate) => fs.existsSync(candidate)) || ''
}

async function run() {
  const { url, expect, screenshotDir } = parseArgs(process.argv.slice(2))
  if (!url) {
    throw new Error('missing --url')
  }

  const executablePath = resolveChromePath()
  if (!executablePath) {
    throw new Error('no Chrome or Edge executable found')
  }

  const targetDir = screenshotDir || path.resolve(process.cwd(), '..', '..', '.runtime', 'ui-probes')
  fs.mkdirSync(targetDir, { recursive: true })
  const probeName = new URL(url).pathname.replace(/[\\/]/g, '_').replace(/^_+/, '') || 'root'
  const screenshotPath = path.join(targetDir, `${probeName}.png`)

  const browser = await chromium.launch({
    executablePath,
    headless: true,
  })

  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 960 } })
    const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 25000 })
    await page.screenshot({ path: screenshotPath, fullPage: true })

    const result = await page.evaluate((expectedText) => {
      const bodyText = document.body?.innerText || ''
      const title = document.title || ''
      const sidebar = document.querySelector('aside')
      const heading = document.querySelector('h1')
      const sidebarWidth = sidebar instanceof HTMLElement ? sidebar.offsetWidth : 0
      const headingFontSize = heading instanceof HTMLElement ? Number.parseFloat(getComputedStyle(heading).fontSize || '0') : 0
      const background = getComputedStyle(document.body).backgroundColor || ''
      const styleSheetCount = document.styleSheets.length
      const hasExpectedText = expectedText ? bodyText.includes(expectedText) : true
      const errorMarkers = ['Server Error', 'Cannot find module', 'PageNotFoundError', 'webpack-runtime', 'TypeError:']
      const mojibakeMarkers = ['ä¿¡æ', 'æ™ºèƒ½', 'è®¾ç½®', 'é€šçŸ¥', '\uFFFD']

      let hasLoadedStyles = styleSheetCount > 0
      if (!hasLoadedStyles) {
        hasLoadedStyles = Array.from(document.querySelectorAll('style,link[rel="stylesheet"]')).length > 0
      }

      return {
        title,
        bodyPreview: bodyText.slice(0, 240),
        sidebarWidth,
        headingFontSize,
        background,
        styleSheetCount,
        hasExpectedText,
        hasLoadedStyles,
        hasErrorMarker: errorMarkers.some((marker) => bodyText.includes(marker)),
        hasMojibake: mojibakeMarkers.some((marker) => bodyText.includes(marker) || title.includes(marker)),
      }
    }, expect)

    const ok =
      Boolean(response && response.status() === 200) &&
      result.hasExpectedText &&
      result.hasLoadedStyles &&
      !result.hasErrorMarker &&
      !result.hasMojibake &&
      result.sidebarWidth >= 180 &&
      result.headingFontSize >= 24

    console.log(
      JSON.stringify({
        ok,
        status: response?.status() || 0,
        url,
        screenshotPath,
        ...result,
        error: ok ? null : 'browser ui probe detected layout, style, or encoding regression',
      }),
    )
  } finally {
    await browser.close()
  }
}

run().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
})
