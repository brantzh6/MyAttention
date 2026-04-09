'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api-client'
import { FlaskConical, Link, Search, BookOpen, Target, Layers, AlertCircle, CheckCircle2, ChevronDown, ChevronUp, Languages } from 'lucide-react'

interface IKEWorkspaceManagerProps {
  report: any | null
  closure: any | null
  proceduralMemoryCandidate: any | null
  runtimeSurface: any | null
  runtimeError: string | null
  runtimePreflight: any | null
  runtimePreflightError: string | null
  loadError: string | null
  isB4?: boolean
}

type LanguageMode = 'bilingual' | 'chinese' | 'english'

// Deterministic content translations for current harness benchmark story
// This is NOT a general i18n framework - just bounded mappings for current benchmark
const contentTranslations: Record<string, { zh: string }> = {
  // Signal summary (B1)
  "Detected 6 benchmark entities related to 'harness'. Top signals: LeoYeAI/openclaw-master-skills, leoyeai, slowmist, slowmist/openclaw-security-practice-guide, netease-youdao/lobsterai.": {
    zh: '检测到 6 个与 "harness" 相关的基准实体。主要信号：LeoYeAI/openclaw-master-skills、leoyeai、slowmist、slowmist/openclaw-security-practice-guide、netease-youdao/lobsterai。',
  },
  // Concept summary (B1 Knowledge)
  "In this benchmark context, 'harness' refers to evaluation and testing infrastructure for AI agents and agent frameworks, as evidenced by 6 detected entities. The 'harness' concept relates to openclaw, AI agent frameworks, evaluation/testing, and research practice, with evidence from: openclaw ecosystem (LeoYeAI/openclaw-master-skills), AI agent space (LeoYeAI/openclaw-master-skills), AI agent space (leoyeai), openclaw ecosystem (slowmist/openclaw-security-practice-guide). Unlike generic testing frameworks, 'harness' shows both individual practitioners (2 persons) and project repositories (3 repos), suggesting a practice-oriented approach rather than purely tool-centric. Organizational participation (1 organizations) distinguishes 'harness' from purely academic or hobbyist evaluation approaches. Evidence anchors: LeoYeAI/openclaw-master-skills, leoyeai, slowmist, slowmist/openclaw-security-practice-guide, netease-youdao/lobsterai.": {
    zh: '在此基准上下文中，"harness" 指的是 AI 代理和代理框架的评估和测试基础设施，由检测到的 6 个实体证明。"harness" 概念与 openclaw、AI 代理框架、评估/测试和研究实践相关，证据来自：openclaw 生态系统（LeoYeAI/openclaw-master-skills）、AI 代理空间（LeoYeAI/openclaw-master-skills）、AI 代理空间（leoyeai）、openclaw 生态系统（slowmist/openclaw-security-practice-guide）。与通用测试框架不同，"harness" 展示了个人实践者（2 人）和项目仓库（3 个），表明是面向实践的方法而非纯工具导向。组织参与（1 个组织）使 "harness" 区别于纯学术或爱好导向的评估方法。证据锚点：LeoYeAI/openclaw-master-skills、leoyeai、slowmist、slowmist/openclaw-security-practice-guide、netease-youdao/lobsterai。',
  },
  // Best fit interpretation (B3)
  "Interpretation C: harness as integration layer connecting agents to existing test frameworks and evaluation workflows. Best fit because: (1) aligns with 'make active work surface understandable' gap, (2) supports 'controlled delegation' through structured evaluation interfaces, (3) matches practice-oriented evidence from B1 benchmark entities.": {
    zh: '解释 C：harness 作为将代理连接到现有测试框架和评估工作流的集成层。最匹配因为：(1) 与 "使活跃工作表面可理解" 差距对齐，(2) 通过结构化评估接口支持 "受控委托"，(3) 与 B1 基准实体的面向实践证据匹配。',
  },
  // Gap descriptions (B2)
  'Make the active work surface (projects, tasks, context) understandable to the agent': {
    zh: '使活跃工作表面（项目、任务、上下文）对代理可理解',
  },
  'Reduce token pressure through controlled delegation to specialized agents': {
    zh: '通过对专业代理的受控委托减少 token 压力',
  },
  // Specific contributions (B2)
  "Concept evidence for 'harness' shows 1 keyword matches with gap 'make active work surface understandable', but no specific entities directly support this gap.": {
    zh: '"harness" 的概念证据显示与差距 "使活跃工作表面可理解" 有 1 个关键词匹配，但没有特定实体直接支持此差距。',
  },
  "Concept evidence for 'harness' shows 1 keyword matches with gap 'reduce token pressure through controlled delegation', but no specific entities directly support this gap.": {
    zh: '"harness" 的概念证据显示与差距 "通过对专业代理的受控委托减少 token 压力" 有 1 个关键词匹配，但没有特定实体直接支持此差距。',
  },
  // Recommendation rationale (B2)
  "Recommendation for 'harness': study level. Aligned with 2 mainline gap(s): make active work surface understandable, reduce token pressure through controlled delegation. Evidence suggests potential value but requires validation. Gap alignment present (2 gaps) Evidence still indirect, no direct repository validation Evidence includes authoritative, maintainer, or implementation sources.": {
    zh: '对 "harness" 的建议：研究级别。与 2 个主要差距对齐：使活跃工作表面可理解、通过对专业代理的受控委托减少 token 压力。证据表明潜在价值但需要验证。存在差距对齐（2 个差距）证据仍为间接，无直接仓库验证证据包括权威、维护者或实现来源。',
  },
  // Next action (B3)
  "Proceed with B2-S4 trigger packet (B2-S4-HARNESS-STUDY-8098e069). Task type: study. Focus: Inspect the 'slowmist/openclaw-security-practice-guide' repository related to 'harness'. Focus on do...": {
    zh: '继续执行 B2-S4 触发包（B2-S4-HARNESS-STUDY-8098e069）。任务类型：研究。重点：检查与 "harness" 相关的 "slowmist/openclaw-security-practice-guide" 仓库。重点在于...',
  },
  // Blockers (B2)
  'No direct repository content validation yet': {
    zh: '尚无直接仓库内容验证',
  },
  'Evidence remains indirect (trend-level only)': {
    zh: '证据仍为间接（仅趋势级别）',
  },
  'Requires hands-on evaluation to advance to prototype': {
    zh: '需要动手评估才能推进到原型阶段',
  },
  // Closure summary
  'Real bounded study closure for harness: documentation-level evidence supports continued study, not prototype. Next step is one more implementation sample plus adaptation analysis.': {
    zh: 'harness 的真实限定研究闭环：文档级别证据支持继续研究，而非原型。下一步是再增加一个实现样本加上适应性分析。',
  },
  // Study findings
  'Repository is agent-facing and designed for high-privilege OpenClaw operations rather than a human-only hardening checklist.': {
    zh: '仓库面向代理设计，用于高权限 OpenClaw 操作，而非纯人工加固清单。',
  },
  'Three-tier pre-action / in-action / post-action structure provides a concrete evaluation and audit workflow shape.': {
    zh: '三层操作前/操作中/操作后结构提供了具体的评估和审计工作流形状。',
  },
  'Nightly explicit audits with 13 core metrics show a reusable pattern for evaluation visibility and no-silent-pass reporting.': {
    zh: '具有 13 个核心指标的夜间显式审计展示了评估可见性和无静默通过报告的可重用模式。',
  },
  'Validation guide includes explicit red-team style tests for prompt injection, hidden installs, destructive actions, exfiltration, persistence, and audit verification.': {
    zh: '验证指南包括针对提示注入、隐藏安装、破坏性操作、数据外泄、持久化和审计验证的显式红队风格测试。',
  },
  'High-risk actions require human confirmation, preserving a clear human responsibility boundary.': {
    zh: '高风险操作需要人工确认，保持清晰的人工责任边界。',
  },
  'Evidence is documentation-level only; no runtime integration or hands-on validation was performed in this study.': {
    zh: '证据仅为文档级别；本研究未进行运行时集成或动手验证。',
  },
  // Decision handoff justification
  'The repository provides concrete evaluation and audit patterns relevant to evolution-layer operations, but evidence remains security-specific, documentation-only, and insufficient for prototype escalation. Continue study with one more implementation sample and explicit adaptation analysis.': {
    zh: '该仓库提供了与进化层操作相关的具体评估和审计模式，但证据仍然是安全特定的、仅文档级别，且不足以支持原型升级。继续研究，增加一个实现样本和明确的适应性分析。',
  },
  // Procedural memory lesson
  'A pre-action / in-action / post-action evaluation structure is more inspectable than a single pass-fail gate when reviewing agent behavior.': {
    zh: '在审查代理行为时，操作前/操作中/操作后的评估结构比单一的通过/失败门更可检查。',
  },
  // Why it mattered
  "The reviewed harness study found a concrete audit workflow shape that maps to IKE's evolution-layer evaluation operations, but only partially and with security-specific limits.": {
    zh: '审查的 harness 研究发现了一个具体的审计工作流形状，可映射到 IKE 的进化层评估操作，但仅部分映射且具有安全特定限制。',
  },
  // How to apply
  'When designing IKE evaluation operations, prefer explicit preflight checks, execution-time checks, and closure/audit checks instead of a single aggregated result gate.': {
    zh: '设计 IKE 评估操作时，优先使用显式的预检检查、执行时检查和闭环/审计检查，而非单一的聚合结果门。',
  },
  // Procedural memory notes
  'This is an explicit reviewed benchmark closure payload candidate, not an automatically inferred memory.': {
    zh: '这是一个显式审查的基准闭环负载候选，而非自动推断的记忆。',
  },
  'It should be consumed only through the truthful procedural-memory payload adapter.': {
    zh: '它应仅通过真实的程序性记忆负载适配器消费。',
  },
}

function translateContent(text: string | null | undefined, mode: LanguageMode): { en: string; zh: string } {
  const enText = text || ''
  const translation = text ? contentTranslations[text] : undefined
  const zhText = translation?.zh || enText
  return { en: enText, zh: zhText }
}

const labels = {
  en: {
    pageTitle: 'IKE Benchmark Story',
    currentStatus: 'Current Benchmark Status',
    ikeLayer: 'IKE Layer',
    applicability: 'Applicability',
    confidence: 'Confidence',
    entities: 'Entities',
    conceptTitle: (topic: string) => `What is '${topic}'?`,
    bestFitInterpretation: 'Best Fit Interpretation',
    conceptDefining: 'Concept Defining',
    conceptDefiningDesc: 'Entities that define, originate, or fundamentally shape the concept',
    ecosystemRelevant: 'Ecosystem Relevant',
    ecosystemRelevantDesc: 'Entities that shape the surrounding ecosystem, adoption patterns, or discourse',
    implementationRelevant: 'Implementation Relevant',
    implementationRelevantDesc: 'Entities directly relevant to implementing or applying in this project',
    noEntries: 'No entries',
    gapAlignment: 'Project Gap Alignment',
    relevance: 'relevance',
    noGaps: 'No gap mappings available',
    recommendation: 'Recommendation & Next Action',
    recommendationLevel: 'Recommendation Level',
    noRationale: 'No rationale available',
    nextAction: 'Bounded Next Action',
    noNextAction: 'No next action defined',
    blockers: 'Blockers',
    closureExample: 'Study Closure',
    studyFindings: 'Study Findings',
    noFindings: 'No findings',
    status: 'Status',
    time: 'Time',
    decisionHandoff: 'Decision Handoff',
    type: 'Type',
    justification: 'Justification',
    confidenceLabel: 'Confidence',
    noClosureSummary: 'No closure summary available',
    inspectTools: 'Advanced Inspect Tools',
    experimental: 'Experimental',
    inspectToolsDesc: 'These tools are for debugging and validation. All objects are provisional and not durably stored.',
    observationInspect: 'Observation Inspect',
    observationInspectDesc: 'Materialize an Observation from a feed_item JSON payload.',
    feedItemJson: 'Feed Item JSON',
    inspectObservation: 'Inspect Observation',
    inspecting: 'Inspecting...',
    chainInspect: 'Chain Inspect',
    chainInspectDesc: 'Inspect a loop chain artifact by artifact_id.',
    artifactId: 'Artifact ID',
    inspectChain: 'Inspect Chain',
    complete: 'Complete',
    incomplete: 'Incomplete',
    completeness: 'Completeness',
    objects: 'Objects',
    bilingual: 'Bilingual',
    chineseOnly: 'Chinese',
    englishOnly: 'English',
    noSignalSummary: 'No signal summary available',
    noConceptSummary: 'No concept summary available',
    evidenceQuality: 'Evidence Quality',
    evidenceLayerDistribution: 'Evidence Layer Distribution',
    strongestEvidence: 'Strongest Evidence',
    weakestEvidence: 'Weakest Evidence',
    taggedEntities: 'Tagged Entities by Evidence Layer',
    noEvidenceData: 'No evidence layer data available',
    layerCount: 'entities',
    b4ReportBadge: 'B4-Aware',
    b3ReportBadge: 'B3',
    proceduralMemoryCandidate: 'Procedural Memory Candidate',
    candidateDesc: 'Reviewed benchmark closure payload (candidate, not accepted durable memory)',
    candidateLesson: 'Lesson',
    candidateWhyItMattered: 'Why It Mattered',
    candidateHowToApply: 'How to Apply',
    candidateConfidence: 'Confidence',
    candidateSource: 'Source Artifact',
    candidateStatus: 'Status',
    candidateNotes: 'Notes',
    sendToRuntimeReview: 'Send To Runtime Review',
    sendingToRuntimeReview: 'Sending To Runtime Review...',
    runtimeReviewQueued: 'Queued for runtime review',
    runtimeReviewDesc: 'This sends the reviewed benchmark candidate into runtime as a pending_review packet only.',
    runtimeSurface: 'Runtime Surface',
    runtimeSurfaceDesc: 'Narrow runtime-backed visible surface derived from runtime truth only.',
    runtimeUnavailable: 'Runtime surface not available yet',
    runtimePreflight: 'Service Preflight',
    runtimePreflightDesc: 'Strict machine-readable live-proof status using the preferred repo-owned service baseline.',
    runtimePreflightStatus: 'Preflight Status',
    runtimePreflightOwner: 'Preferred Owner',
    runtimePreflightOwnerChain: 'Owner Chain',
    runtimePreflightRepoLauncher: 'Repo Launcher',
    runtimePreflightControllerAcceptability: 'Controller Acceptability',
    runtimePreflightCodeFreshness: 'Code Freshness',
    runtimePreflightCanonicalLaunch: 'Canonical Launch',
    runtimePreflightSummary: 'Service Summary',
    runtimePreflightMismatch: 'Preferred owner mismatch detected',
    runtimePreflightUnavailable: 'Service preflight not available',
    runtimeActivationDesc: 'Create or recover the explicit runtime project surface for this workspace.',
    activateRuntime: 'Activate Runtime Surface',
    activatingRuntime: 'Activating Runtime Surface...',
    project: 'Project',
    phase: 'Phase',
    activeTasks: 'Active Tasks',
    waitingTasks: 'Waiting Tasks',
    trustedPackets: 'Trusted Packets',
    currentFocus: 'Current Focus',
    blockersSummary: 'Blockers',
    nextStepsSummary: 'Next Steps',
  },
  zh: {
    pageTitle: 'IKE 基准故事',
    currentStatus: '当前基准状态',
    ikeLayer: 'IKE 层',
    applicability: '适用性',
    confidence: '置信度',
    entities: '实体数',
    conceptTitle: (topic: string) => `什么是 '${topic}'？`,
    bestFitInterpretation: '最佳匹配解释',
    conceptDefining: '概念定义层',
    conceptDefiningDesc: '定义、起源或从根本上塑造该概念的实体',
    ecosystemRelevant: '生态相关层',
    ecosystemRelevantDesc: '塑造周围生态、采用模式或话语的实体',
    implementationRelevant: '实现相关层',
    implementationRelevantDesc: '与在项目中实现或应用直接相关的实体',
    noEntries: '无条目',
    gapAlignment: '项目差距对齐',
    relevance: '相关性',
    noGaps: '无差距映射',
    recommendation: '建议与下一步行动',
    recommendationLevel: '建议级别',
    noRationale: '无可用理由',
    nextAction: '限定性下一步行动',
    noNextAction: '未定义下一步行动',
    blockers: '阻碍因素',
    closureExample: '研究闭环',
    studyFindings: '研究发现',
    noFindings: '无发现',
    status: '状态',
    time: '时间',
    decisionHandoff: '决策移交',
    type: '类型',
    justification: '理由',
    confidenceLabel: '置信度',
    noClosureSummary: '无闭环摘要',
    inspectTools: '高级检查工具',
    experimental: '实验性',
    inspectToolsDesc: '这些工具用于调试和验证。所有对象都是临时的，不会持久存储。',
    observationInspect: '观察检查',
    observationInspectDesc: '从 feed_item JSON 负载具体化观察。',
    feedItemJson: 'Feed Item JSON',
    inspectObservation: '检查观察',
    inspecting: '检查中...',
    chainInspect: '链检查',
    chainInspectDesc: '按 artifact_id 检查循环链工件。',
    artifactId: 'Artifact ID',
    inspectChain: '检查链',
    complete: '完整',
    incomplete: '不完整',
    completeness: '完整性',
    objects: '对象数',
    bilingual: '中英对照',
    chineseOnly: '仅中文',
    englishOnly: '仅英文',
    noSignalSummary: '无可用信号摘要',
    noConceptSummary: '无可用概念摘要',
    evidenceQuality: '证据质量',
    evidenceLayerDistribution: '证据层分布',
    strongestEvidence: '最强证据',
    weakestEvidence: '最弱证据',
    taggedEntities: '按证据层标记的实体',
    noEvidenceData: '无证据层数据',
    layerCount: '个实体',
    b4ReportBadge: 'B4 证据感知',
    b3ReportBadge: 'B3',
    proceduralMemoryCandidate: '程序性记忆候选',
    candidateDesc: '已审查的基准闭环负载（候选，非已接受的持久记忆）',
    candidateLesson: '经验教训',
    candidateWhyItMattered: '为何重要',
    candidateHowToApply: '如何应用',
    candidateConfidence: '置信度',
    candidateSource: '源工件',
    candidateStatus: '状态',
    candidateNotes: '备注',
    sendToRuntimeReview: '发送到 Runtime 审查队列',
    sendingToRuntimeReview: '正在发送到 Runtime 审查队列...',
    runtimeReviewQueued: '已进入 Runtime 审查队列',
    runtimeReviewDesc: '这只会把已审查的 benchmark 候选送入 runtime 的 pending_review packet，不会直接变成可信记忆。',
    runtimeSurface: 'Runtime 表面',
    runtimeSurfaceDesc: '仅由 runtime 真相推导出的窄可见表面。',
    runtimeUnavailable: 'Runtime 表面暂不可用',
    runtimeActivationDesc: '为当前工作区创建或恢复显式的 runtime 项目表面。',
    activateRuntime: '激活 Runtime 表面',
    activatingRuntime: '正在激活 Runtime 表面...',
    project: '项目',
    phase: '阶段',
    activeTasks: '活跃任务',
    waitingTasks: '等待任务',
    trustedPackets: '可信记忆包',
    currentFocus: '当前焦点',
    blockersSummary: '阻塞摘要',
    nextStepsSummary: '下一步摘要',
  },
}

function BilingualBlock({
  en,
  zh,
  mode,
  className = '',
}: {
  en: React.ReactNode
  zh: React.ReactNode
  mode: LanguageMode
  className?: string
}) {
  if (mode === 'english') {
    return <span className={className}>{en}</span>
  }
  if (mode === 'chinese') {
    return <span className={className}>{zh}</span>
  }
  return (
    <span className={`grid gap-2 md:grid-cols-2 md:gap-4 ${className}`}>
      <span className="text-muted-foreground md:border-r md:pr-4">{en}</span>
      <span className="text-foreground">{zh}</span>
    </span>
  )
}

export default function IKEWorkspaceManager({
  report,
  closure,
  proceduralMemoryCandidate,
  runtimeSurface,
  runtimeError,
  runtimePreflight,
  runtimePreflightError,
  loadError,
  isB4 = false,
}: IKEWorkspaceManagerProps) {
  const [observationJson, setObservationJson] = useState(`{
  "source_id": "source-example",
  "title": "Example Observation",
  "summary": "This is a test observation for the IKE workspace.",
  "fetched_at": "2026-03-29T12:00:00Z",
  "url": "https://example.com/article"
}`)
  const [artifactId, setArtifactId] = useState('')
  const [observationResult, setObservationResult] = useState<any>(null)
  const [chainResult, setChainResult] = useState<any>(null)
  const [observationError, setObservationError] = useState<string | null>(null)
  const [chainError, setChainError] = useState<string | null>(null)
  const [isLoadingObservation, setIsLoadingObservation] = useState(false)
  const [isLoadingChain, setIsLoadingChain] = useState(false)
  const [showInspectTools, setShowInspectTools] = useState(false)
  const [languageMode, setLanguageMode] = useState<LanguageMode>('bilingual')
  const [isBootstrappingRuntime, setIsBootstrappingRuntime] = useState(false)
  const [runtimeActivationError, setRuntimeActivationError] = useState<string | null>(null)
  const [isImportingBenchmarkCandidate, setIsImportingBenchmarkCandidate] = useState(false)
  const [benchmarkImportError, setBenchmarkImportError] = useState<string | null>(null)
  const [benchmarkImportResult, setBenchmarkImportResult] = useState<any>(null)

  const handleInspectObservation = async () => {
    setIsLoadingObservation(true)
    setObservationError(null)
    setObservationResult(null)

    try {
      const feedItem = JSON.parse(observationJson)
      const result = await apiClient.inspectObservation(feedItem)
      setObservationResult(result)
    } catch (err: any) {
      setObservationError(err.message || 'Failed to inspect observation')
    } finally {
      setIsLoadingObservation(false)
    }
  }

  const handleInspectChain = async () => {
    setIsLoadingChain(true)
    setChainError(null)
    setChainResult(null)

    try {
      if (!artifactId.trim()) {
        throw new Error('Please enter an artifact ID')
      }
      const result = await apiClient.inspectChain(artifactId.trim())
      setChainResult(result)
    } catch (err: any) {
      setChainError(err.message || 'Failed to inspect chain')
    } finally {
      setIsLoadingChain(false)
    }
  }

  const handleActivateRuntimeSurface = async () => {
    setIsBootstrappingRuntime(true)
    setRuntimeActivationError(null)

    try {
      await apiClient.bootstrapRuntimeProjectSurface({
        project_key: 'myattention-runtime-mainline',
        title: 'MyAttention Runtime Mainline',
        current_phase: 'R2-E',
        priority: 1,
      })
      window.location.reload()
    } catch (err: any) {
      setRuntimeActivationError(err.message || 'Failed to activate runtime surface')
    } finally {
      setIsBootstrappingRuntime(false)
    }
  }

  const handleImportBenchmarkCandidate = async () => {
    if (!proceduralMemoryCandidate) return
    setIsImportingBenchmarkCandidate(true)
    setBenchmarkImportError(null)
    setBenchmarkImportResult(null)

    try {
      const result = await apiClient.importRuntimeBenchmarkCandidate({
        project_key: runtimeSurface?.project_key || 'myattention-runtime-mainline',
        candidate_payload: proceduralMemoryCandidate,
      })
      setBenchmarkImportResult(result?.data ?? result)
    } catch (err: any) {
      setBenchmarkImportError(err.message || 'Failed to import benchmark candidate')
    } finally {
      setIsImportingBenchmarkCandidate(false)
    }
  }

  const getRecommendationColor = (level: string) => {
    switch (level) {
      case 'prototype': return 'bg-green-100 text-green-800 border-green-300'
      case 'study': return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'observe': return 'bg-gray-100 text-gray-800 border-gray-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getPreflightBadgeClass = (status: string | undefined) => {
    switch (status) {
      case 'ready': return 'bg-green-100 text-green-800 border-green-300'
      case 'ambiguous': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'down': return 'bg-red-100 text-red-800 border-red-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const topic = report?.bundle?.topic || 'unknown'
  const bundle = report?.bundle
  const knowledge = report?.knowledge
  const tiers = report?.tiers
  const gaps = report?.gaps
  const recommendation = report?.recommendation
  const deepening = report?.deepening
  const closureData = closure || report?.closure_example

  if (loadError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <h2 className="text-xl font-semibold">
              <BilingualBlock
                en={labels.en.pageTitle}
                zh={labels.zh.pageTitle}
                mode={languageMode}
              />
            </h2>
          </div>
        </div>
        <div className="rounded-lg border border-red-300 bg-red-50 p-6">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <h3 className="font-semibold text-red-800">Unable to Load Benchmark Data</h3>
          </div>
          <p className="text-sm text-red-700">{loadError}</p>
          <p className="text-xs text-red-600 mt-2">
            Ensure the benchmark artifact files exist in .runtime/benchmarks/
          </p>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-primary" />
          <h2 className="text-xl font-semibold">
            <BilingualBlock
              en={labels.en.pageTitle}
              zh={labels.zh.pageTitle}
              mode={languageMode}
            />
          </h2>
        </div>
        <div className="rounded-lg border bg-card p-6 text-center">
          <p className="text-muted-foreground">No benchmark data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Language Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-primary" />
          <h2 className="text-xl font-semibold">
            <BilingualBlock
              en={`IKE Benchmark Story: ${topic}`}
              zh={`IKE 基准故事：${topic}`}
              mode={languageMode}
            />
          </h2>
          <span className={`ml-2 inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium ${getRecommendationColor(recommendation?.level || 'observe')}`}>
            {(recommendation?.level || 'observe').toUpperCase()}
          </span>
          {isB4 ? (
            <span className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium bg-primary/10 text-primary">
              {languageMode === 'chinese' ? labels.zh.b4ReportBadge : labels.en.b4ReportBadge}
            </span>
          ) : (
            <span className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium bg-secondary">
              {languageMode === 'chinese' ? labels.zh.b3ReportBadge : labels.en.b3ReportBadge}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Languages className="h-4 w-4 text-muted-foreground" />
          <div className="flex rounded-md border">
            <button
              onClick={() => setLanguageMode('bilingual')}
              className={`px-3 py-1.5 text-xs font-medium first:rounded-l-md last:rounded-r-md ${languageMode === 'bilingual' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-muted'}`}
            >
              {labels.en.bilingual}
            </button>
            <button
              onClick={() => setLanguageMode('chinese')}
              className={`px-3 py-1.5 text-xs font-medium border-l first:rounded-l-md last:rounded-r-md ${languageMode === 'chinese' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-muted'}`}
            >
              {labels.zh.chineseOnly}
            </button>
            <button
              onClick={() => setLanguageMode('english')}
              className={`px-3 py-1.5 text-xs font-medium border-l first:rounded-l-md last:rounded-r-md ${languageMode === 'english' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-muted'}`}
            >
              {labels.en.englishOnly}
            </button>
          </div>
        </div>
      </div>

      {/* Runtime Surface Panel */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <h3 className="font-semibold text-lg">
              <BilingualBlock
                en={labels.en.runtimeSurface}
                zh={labels.zh.runtimeSurface}
                mode={languageMode}
              />
            </h3>
            <p className="text-sm text-muted-foreground">
              <BilingualBlock
                en={labels.en.runtimeSurfaceDesc}
                zh={labels.zh.runtimeSurfaceDesc}
                mode={languageMode}
              />
            </p>
          </div>
          <span className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium bg-primary/10 text-primary">
            R2-E1
          </span>
        </div>

          {runtimeSurface ? (
            <div className="mt-4 space-y-4">
              <div className="rounded-md border p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <p className="text-xs font-medium">
                      <BilingualBlock
                        en={labels.en.runtimePreflight}
                        zh={(labels.zh as any).runtimePreflight || labels.en.runtimePreflight}
                        mode={languageMode}
                      />
                    </p>
                    <p className="text-xs text-muted-foreground">
                      <BilingualBlock
                        en={labels.en.runtimePreflightDesc}
                        zh={(labels.zh as any).runtimePreflightDesc || labels.en.runtimePreflightDesc}
                        mode={languageMode}
                      />
                    </p>
                  </div>
                  <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium ${getPreflightBadgeClass(runtimePreflight?.status)}`}>
                    {runtimePreflight?.status || 'unavailable'}
                  </span>
                </div>
                {runtimePreflight ? (
                  <div className="mt-3 space-y-2 text-sm">
                    <p>
                      <span className="font-medium">
                        <BilingualBlock
                          en={`${labels.en.runtimePreflightOwner}: `}
                          zh={`${((labels.zh as any).runtimePreflightOwner || labels.en.runtimePreflightOwner)}: `}
                          mode={languageMode}
                        />
                      </span>
                      {runtimePreflight?.details?.preferred_owner?.status || 'N/A'}
                    </p>
                    <p>
                      <span className="font-medium">
                        <BilingualBlock
                          en={`${labels.en.runtimePreflightOwnerChain}: `}
                          zh={`${((labels.zh as any).runtimePreflightOwnerChain || labels.en.runtimePreflightOwnerChain)}: `}
                          mode={languageMode}
                        />
                      </span>
                      {runtimePreflight?.owner_chain?.status || runtimePreflight?.details?.owner_chain?.status || 'N/A'}
                    </p>
                    <p>
                      <span className="font-medium">
                        <BilingualBlock
                          en={`${labels.en.runtimePreflightRepoLauncher}: `}
                          zh={`${((labels.zh as any).runtimePreflightRepoLauncher || labels.en.runtimePreflightRepoLauncher)}: `}
                          mode={languageMode}
                        />
                      </span>
                      {runtimePreflight?.repo_launcher?.status || runtimePreflight?.details?.repo_launcher?.status || 'N/A'}
                    </p>
                    <p>
                      <span className="font-medium">
                        <BilingualBlock
                          en={`${labels.en.runtimePreflightControllerAcceptability}: `}
                          zh={`${((labels.zh as any).runtimePreflightControllerAcceptability || labels.en.runtimePreflightControllerAcceptability)}: `}
                          mode={languageMode}
                        />
                      </span>
                      {runtimePreflight?.controller_acceptability?.status || runtimePreflight?.details?.controller_acceptability?.status || 'N/A'}
                    </p>
                    <p>
                      <span className="font-medium">
                        <BilingualBlock
                          en={`${labels.en.runtimePreflightCodeFreshness}: `}
                          zh={`${((labels.zh as any).runtimePreflightCodeFreshness || labels.en.runtimePreflightCodeFreshness)}: `}
                          mode={languageMode}
                        />
                      </span>
                      {runtimePreflight?.details?.code_freshness?.status || 'N/A'}
                    </p>
                    <p>
                      <span className="font-medium">
                        <BilingualBlock
                          en={`${labels.en.runtimePreflightCanonicalLaunch}: `}
                          zh={`${((labels.zh as any).runtimePreflightCanonicalLaunch || labels.en.runtimePreflightCanonicalLaunch)}: `}
                          mode={languageMode}
                        />
                      </span>
                      <span className="break-all">{runtimePreflight?.details?.canonical_launch?.command_line || 'N/A'}</span>
                    </p>
                    <p>
                      <span className="font-medium">
                        <BilingualBlock
                          en={`${labels.en.runtimePreflightSummary}: `}
                          zh={`${((labels.zh as any).runtimePreflightSummary || labels.en.runtimePreflightSummary)}: `}
                          mode={languageMode}
                        />
                      </span>
                      {runtimePreflight?.summary || 'N/A'}
                    </p>
                    {runtimePreflight?.details?.preferred_owner?.status === 'preferred_mismatch' && (
                      <p className="text-xs text-yellow-700">
                        <BilingualBlock
                          en={labels.en.runtimePreflightMismatch}
                          zh={(labels.zh as any).runtimePreflightMismatch || labels.en.runtimePreflightMismatch}
                          mode={languageMode}
                        />
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="mt-3 text-xs text-muted-foreground">
                    {runtimePreflightError || ((languageMode === 'chinese' ? (labels.zh as any).runtimePreflightUnavailable : labels.en.runtimePreflightUnavailable) || labels.en.runtimePreflightUnavailable)}
                  </p>
                )}
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-md bg-muted p-4">
                <p className="text-xs font-medium mb-2">
                  <BilingualBlock en={labels.en.project} zh={labels.zh.project} mode={languageMode} />
                </p>
                <p className="text-sm font-semibold">{runtimeSurface.title}</p>
                <p className="text-xs text-muted-foreground mt-1">{runtimeSurface.project_key}</p>
              </div>
              <div className="rounded-md bg-muted p-4">
                <p className="text-xs font-medium mb-2">
                  <BilingualBlock en={labels.en.phase} zh={labels.zh.phase} mode={languageMode} />
                </p>
                <p className="text-sm font-semibold">{runtimeSurface.current_phase || 'N/A'}</p>
                <p className="text-xs text-muted-foreground mt-1">{runtimeSurface.status || 'N/A'}</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-md border p-3">
                <p className="text-xs text-muted-foreground">
                  <BilingualBlock en={labels.en.activeTasks} zh={labels.zh.activeTasks} mode={languageMode} />
                </p>
                <p className="text-lg font-semibold">{runtimeSurface.active_tasks?.length || 0}</p>
              </div>
              <div className="rounded-md border p-3">
                <p className="text-xs text-muted-foreground">
                  <BilingualBlock en={labels.en.waitingTasks} zh={labels.zh.waitingTasks} mode={languageMode} />
                </p>
                <p className="text-lg font-semibold">{runtimeSurface.waiting_tasks?.length || 0}</p>
              </div>
              <div className="rounded-md border p-3">
                <p className="text-xs text-muted-foreground">
                  <BilingualBlock en={labels.en.trustedPackets} zh={labels.zh.trustedPackets} mode={languageMode} />
                </p>
                <p className="text-lg font-semibold">{runtimeSurface.trusted_packets?.length || 0}</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-md border p-4">
                <p className="text-xs font-medium mb-2">
                  <BilingualBlock en={labels.en.currentFocus} zh={labels.zh.currentFocus} mode={languageMode} />
                </p>
                <p className="text-sm text-muted-foreground">{runtimeSurface.current_focus || 'N/A'}</p>
              </div>
              <div className="rounded-md border p-4">
                <p className="text-xs font-medium mb-2">
                  <BilingualBlock en={labels.en.blockersSummary} zh={labels.zh.blockersSummary} mode={languageMode} />
                </p>
                <p className="text-sm text-muted-foreground">{runtimeSurface.blockers_summary || 'N/A'}</p>
              </div>
            </div>

            <div className="rounded-md border p-4">
              <p className="text-xs font-medium mb-2">
                <BilingualBlock en={labels.en.nextStepsSummary} zh={labels.zh.nextStepsSummary} mode={languageMode} />
              </p>
              <p className="text-sm text-muted-foreground">{runtimeSurface.next_steps_summary || 'N/A'}</p>
            </div>
          </div>
        ) : (
          <div className="mt-4 rounded-md border border-yellow-300 bg-yellow-50 p-4">
            <p className="text-sm font-medium text-yellow-800">
              <BilingualBlock
                en={labels.en.runtimeUnavailable}
                zh={labels.zh.runtimeUnavailable}
                mode={languageMode}
              />
            </p>
            <p className="mt-1 text-xs text-yellow-700">
              <BilingualBlock
                en={labels.en.runtimeActivationDesc}
                zh={labels.zh.runtimeActivationDesc}
                mode={languageMode}
              />
            </p>
            {(runtimeError || runtimeActivationError) && (
              <p className="mt-2 text-xs text-yellow-700">{runtimeActivationError || runtimeError}</p>
            )}
            <button
              onClick={handleActivateRuntimeSurface}
              disabled={isBootstrappingRuntime}
              className="mt-3 inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
            >
              {isBootstrappingRuntime
                ? (languageMode === 'chinese' ? labels.zh.activatingRuntime : labels.en.activatingRuntime)
                : (languageMode === 'chinese' ? labels.zh.activateRuntime : labels.en.activateRuntime)}
            </button>
          </div>
        )}
      </div>

      {/* Summary Status Panel */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <h3 className="font-semibold text-lg">
              <BilingualBlock
                en={labels.en.currentStatus}
                zh={labels.zh.currentStatus}
                mode={languageMode}
              />
            </h3>
            {(() => {
              const signalSummary = translateContent(bundle?.signal_summary, languageMode)
              return (
                <BilingualBlock
                  en={signalSummary.en || labels.en.noSignalSummary}
                  zh={signalSummary.zh || labels.zh.noSignalSummary}
                  mode={languageMode}
                />
              )
            })()}
          </div>
          <div className="flex flex-col items-end gap-2">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">
                <BilingualBlock
                  en={labels.en.ikeLayer}
                  zh={labels.zh.ikeLayer}
                  mode={languageMode}
                />
              </span>
            </div>
            <span className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium bg-secondary">
              {deepening?.target_ike_layer || 'N/A'}
            </span>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">
              <BilingualBlock
                en={`${labels.en.applicability}: `}
                zh={`${labels.zh.applicability}: `}
                mode={languageMode}
              />
              <strong>{deepening?.applicability_judgment || 'N/A'}</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">
              <BilingualBlock
                en={`${labels.en.confidence}: `}
                zh={`${labels.zh.confidence}: `}
                mode={languageMode}
              />
              <strong>{((recommendation?.confidence || 0) * 100).toFixed(0)}%</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">
              <BilingualBlock
                en={`${labels.en.entities}: `}
                zh={`${labels.zh.entities}: `}
                mode={languageMode}
              />
              <strong>{bundle?.ranked_entities?.length || tiers?.concept_defining?.entries?.length + tiers?.ecosystem_relevant?.entries?.length + tiers?.implementation_relevant?.entries?.length || 0}</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Concept Definition Card */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="h-5 w-5" />
          <h3 className="font-semibold">
            <BilingualBlock
              en={labels.en.conceptTitle(topic)}
              zh={labels.zh.conceptTitle(topic)}
              mode={languageMode}
            />
          </h3>
        </div>
        <div className="text-sm text-muted-foreground leading-relaxed">
          {(() => {
            const conceptSummary = translateContent(knowledge?.concept_summary, languageMode)
            return (
              <BilingualBlock
                en={conceptSummary.en || labels.en.noConceptSummary}
                zh={conceptSummary.zh || labels.zh.noConceptSummary}
                mode={languageMode}
              />
            )
          })()}
        </div>
        <div className="mt-4 p-3 rounded-md bg-muted">
          <p className="text-xs font-medium mb-1">
            <BilingualBlock
              en={labels.en.bestFitInterpretation}
              zh={labels.zh.bestFitInterpretation}
              mode={languageMode}
            />
          </p>
          {(() => {
            const interpretation = translateContent(deepening?.best_fit_interpretation, languageMode)
            return (
              <BilingualBlock en={interpretation.en || 'N/A'} zh={interpretation.zh || 'N/A'} mode={languageMode} />
            )
          })()}
        </div>
      </div>

      {/* Entity Tiers */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-lg border bg-card p-4">
          <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs">1</span>
            <BilingualBlock
              en={labels.en.conceptDefining}
              zh={labels.zh.conceptDefining}
              mode={languageMode}
            />
          </h4>
          <p className="text-xs text-muted-foreground mb-3">
            {languageMode === 'chinese' ? labels.zh.conceptDefiningDesc : languageMode === 'english' ? labels.en.conceptDefiningDesc : (
              <span><span className="text-muted-foreground">{labels.en.conceptDefiningDesc}</span><span className="ml-2 text-foreground">{labels.zh.conceptDefiningDesc}</span></span>
            )}
          </p>
          <ul className="space-y-2">
            {tiers?.concept_defining?.entries?.map((entry: any, idx: number) => (
              <li key={idx} className="text-xs">
                <span className="font-medium">{entry.entity_name}</span>
                <span className="ml-2 inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px]">{entry.entity_type}</span>
              </li>
            )) || <li className="text-xs text-muted-foreground">{languageMode === 'chinese' ? labels.zh.noEntries : labels.en.noEntries}</li>}
          </ul>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-secondary text-secondary-foreground text-xs">2</span>
            <BilingualBlock
              en={labels.en.ecosystemRelevant}
              zh={labels.zh.ecosystemRelevant}
              mode={languageMode}
            />
          </h4>
          <p className="text-xs text-muted-foreground mb-3">
            {languageMode === 'chinese' ? labels.zh.ecosystemRelevantDesc : languageMode === 'english' ? labels.en.ecosystemRelevantDesc : (
              <span><span className="text-muted-foreground">{labels.en.ecosystemRelevantDesc}</span><span className="ml-2 text-foreground">{labels.zh.ecosystemRelevantDesc}</span></span>
            )}
          </p>
          <ul className="space-y-2">
            {tiers?.ecosystem_relevant?.entries?.map((entry: any, idx: number) => (
              <li key={idx} className="text-xs">
                <span className="font-medium">{entry.entity_name}</span>
                <span className="ml-2 inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px]">{entry.entity_type}</span>
              </li>
            )) || <li className="text-xs text-muted-foreground">{languageMode === 'chinese' ? labels.zh.noEntries : labels.en.noEntries}</li>}
          </ul>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent text-accent-foreground text-xs">3</span>
            <BilingualBlock
              en={labels.en.implementationRelevant}
              zh={labels.zh.implementationRelevant}
              mode={languageMode}
            />
          </h4>
          <p className="text-xs text-muted-foreground mb-3">
            {languageMode === 'chinese' ? labels.zh.implementationRelevantDesc : languageMode === 'english' ? labels.en.implementationRelevantDesc : (
              <span><span className="text-muted-foreground">{labels.en.implementationRelevantDesc}</span><span className="ml-2 text-foreground">{labels.zh.implementationRelevantDesc}</span></span>
            )}
          </p>
          <ul className="space-y-2">
            {tiers?.implementation_relevant?.entries?.map((entry: any, idx: number) => (
              <li key={idx} className="text-xs">
                <span className="font-medium">{entry.entity_name}</span>
                <span className="ml-2 inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px]">{entry.entity_type}</span>
              </li>
            )) || <li className="text-xs text-muted-foreground">{languageMode === 'chinese' ? labels.zh.noEntries : labels.en.noEntries}</li>}
          </ul>
        </div>
      </div>

      {/* Gap + Mechanism Section */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Target className="h-5 w-5" />
          <h3 className="font-semibold">
            <BilingualBlock
              en={labels.en.gapAlignment}
              zh={labels.zh.gapAlignment}
              mode={languageMode}
            />
          </h3>
        </div>
        <div className="space-y-4">
          {gaps?.mappings?.map((gap: any, idx: number) => {
            const gapDesc = translateContent(gap.gap_description, languageMode)
            const specContrib = translateContent(gap.specific_contribution, languageMode)
            return (
              <div key={idx} className="rounded-md border p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium">{gap.gap_id}</h4>
                  <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${gap.relevance_score === 'high' ? 'bg-red-100 text-red-700' : gap.relevance_score === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'}`}>
                    {gap.relevance_score} <BilingualBlock en={labels.en.relevance} zh={labels.zh.relevance} mode={languageMode} />
                  </span>
                </div>
                <BilingualBlock en={gapDesc.en} zh={gapDesc.zh} mode={languageMode} />
                <div className="mt-2">
                  <BilingualBlock en={specContrib.en} zh={specContrib.zh} mode={languageMode} />
                </div>
              </div>
            )
          }) || <p className="text-sm text-muted-foreground">{languageMode === 'chinese' ? labels.zh.noGaps : labels.en.noGaps}</p>}
        </div>
      </div>

      {/* Recommendation + Trigger Section */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle2 className="h-5 w-5" />
          <h3 className="font-semibold">
            <BilingualBlock
              en={labels.en.recommendation}
              zh={labels.zh.recommendation}
              mode={languageMode}
            />
          </h3>
        </div>
        <div className="space-y-4">
          <div className={`rounded-md border p-4 ${getRecommendationColor(recommendation?.level || 'observe')}`}>
            <p className="text-sm font-medium mb-2">
              <BilingualBlock
                en={`${labels.en.recommendationLevel}: `}
                zh={`${labels.zh.recommendationLevel}: `}
                mode={languageMode}
              />
              {(recommendation?.level || 'observe').toUpperCase()}
            </p>
            {(() => {
              const rationale = translateContent(recommendation?.rationale, languageMode)
              return <BilingualBlock en={rationale.en || labels.en.noRationale} zh={rationale.zh || labels.zh.noRationale} mode={languageMode} />
            })()}
          </div>
          <div className="rounded-md bg-muted p-4">
            <p className="text-sm font-medium mb-2">
              <BilingualBlock
                en={labels.en.nextAction}
                zh={labels.zh.nextAction}
                mode={languageMode}
              />
            </p>
            {(() => {
              const nextAction = translateContent(deepening?.next_action, languageMode)
              return <BilingualBlock en={nextAction.en || labels.en.noNextAction} zh={nextAction.zh || labels.zh.noNextAction} mode={languageMode} />
            })()}
          </div>
          {recommendation?.blockers?.length > 0 && (
            <div className="rounded-md border border-yellow-300 bg-yellow-50 p-4">
              <p className="text-sm font-medium mb-2 text-yellow-800">
                <BilingualBlock
                  en={labels.en.blockers}
                  zh={labels.zh.blockers}
                  mode={languageMode}
                />
              </p>
              <ul className="text-xs text-yellow-700 space-y-1">
                {recommendation.blockers.map((blocker: string, idx: number) => {
                  const blockerTrans = translateContent(blocker, languageMode)
                  return (
                    <li key={idx}>
                      <BilingualBlock en={blockerTrans.en} zh={blockerTrans.zh} mode={languageMode} />
                    </li>
                  )
                })}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Procedural Memory Candidate Section */}
      {proceduralMemoryCandidate && (
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">
              <BilingualBlock
                en={labels.en.proceduralMemoryCandidate}
                zh={labels.zh.proceduralMemoryCandidate}
                mode={languageMode}
              />
            </h3>
            <span className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-800 border-yellow-300">
              <BilingualBlock en="Candidate" zh="候选" mode={languageMode} />
            </span>
          </div>
          <p className="text-xs text-muted-foreground mb-4">
            <BilingualBlock
              en={labels.en.candidateDesc}
              zh={labels.zh.candidateDesc}
              mode={languageMode}
            />
          </p>
          <div className="mb-4 rounded-md border border-blue-200 bg-blue-50 p-4">
            <p className="text-xs text-blue-800">
              <BilingualBlock
                en={labels.en.runtimeReviewDesc}
                zh={labels.zh.runtimeReviewDesc}
                mode={languageMode}
              />
            </p>
            {benchmarkImportError && (
              <p className="mt-2 text-xs text-red-700">{benchmarkImportError}</p>
            )}
            {benchmarkImportResult && (
              <p className="mt-2 text-xs text-green-700">
                <BilingualBlock
                  en={`${labels.en.runtimeReviewQueued}: ${benchmarkImportResult.memory_packet_id}`}
                  zh={`${labels.zh.runtimeReviewQueued}：${benchmarkImportResult.memory_packet_id}`}
                  mode={languageMode}
                />
              </p>
            )}
            <button
              onClick={handleImportBenchmarkCandidate}
              disabled={isImportingBenchmarkCandidate}
              className="mt-3 inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
            >
              {isImportingBenchmarkCandidate
                ? (languageMode === 'chinese' ? labels.zh.sendingToRuntimeReview : labels.en.sendingToRuntimeReview)
                : (languageMode === 'chinese' ? labels.zh.sendToRuntimeReview : labels.en.sendToRuntimeReview)}
            </button>
          </div>
          <div className="space-y-4">
            <div className="rounded-md bg-muted p-4">
              <p className="text-xs font-medium mb-2">
                <BilingualBlock en={labels.en.candidateLesson} zh={labels.zh.candidateLesson} mode={languageMode} />
              </p>
              {(() => {
                const lesson = translateContent(proceduralMemoryCandidate.lesson, languageMode)
                return <BilingualBlock en={lesson.en} zh={lesson.zh} mode={languageMode} />
              })()}
            </div>
            <div className="rounded-md bg-muted p-4">
              <p className="text-xs font-medium mb-2">
                <BilingualBlock en={labels.en.candidateWhyItMattered} zh={labels.zh.candidateWhyItMattered} mode={languageMode} />
              </p>
              {(() => {
                const whyItMattered = translateContent(proceduralMemoryCandidate.why_it_mattered, languageMode)
                return <BilingualBlock en={whyItMattered.en} zh={whyItMattered.zh} mode={languageMode} />
              })()}
            </div>
            <div className="rounded-md bg-muted p-4">
              <p className="text-xs font-medium mb-2">
                <BilingualBlock en={labels.en.candidateHowToApply} zh={labels.zh.candidateHowToApply} mode={languageMode} />
              </p>
              {(() => {
                const howToApply = translateContent(proceduralMemoryCandidate.how_to_apply, languageMode)
                return <BilingualBlock en={howToApply.en} zh={howToApply.zh} mode={languageMode} />
              })()}
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-md border p-3">
                <p className="text-xs font-medium mb-1">
                  <BilingualBlock en={labels.en.candidateConfidence} zh={labels.zh.candidateConfidence} mode={languageMode} />
                </p>
                <p className="text-sm font-semibold">{((proceduralMemoryCandidate.confidence || 0) * 100).toFixed(0)}%</p>
              </div>
              <div className="rounded-md border p-3">
                <p className="text-xs font-medium mb-1">
                  <BilingualBlock en={labels.en.candidateSource} zh={labels.zh.candidateSource} mode={languageMode} />
                </p>
                <p className="text-xs text-muted-foreground">{proceduralMemoryCandidate.source_artifact_ref}</p>
              </div>
              <div className="rounded-md border p-3">
                <p className="text-xs font-medium mb-1">
                  <BilingualBlock en={labels.en.candidateStatus} zh={labels.zh.candidateStatus} mode={languageMode} />
                </p>
                <span className="inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-800 border-yellow-300">
                  {proceduralMemoryCandidate.status || 'candidate'}
                </span>
              </div>
            </div>
            {proceduralMemoryCandidate.notes && proceduralMemoryCandidate.notes.length > 0 && (
              <div className="rounded-md border border-blue-200 bg-blue-50 p-4">
                <p className="text-xs font-medium mb-2 text-blue-800">
                  <BilingualBlock en={labels.en.candidateNotes} zh={labels.zh.candidateNotes} mode={languageMode} />
                </p>
                <ul className="text-xs text-blue-700 space-y-1">
                  {proceduralMemoryCandidate.notes.map((note: string, idx: number) => {
                    const noteTrans = translateContent(note, languageMode)
                    return (
                      <li key={idx}>
                        <BilingualBlock en={noteTrans.en} zh={noteTrans.zh} mode={languageMode} />
                      </li>
                    )
                  })}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Closure Example Section */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="h-5 w-5" />
          <h3 className="font-semibold">
            <BilingualBlock
              en={labels.en.closureExample}
              zh={labels.zh.closureExample}
              mode={languageMode}
            />
          </h3>
        </div>
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-md bg-muted p-4">
              <p className="text-xs font-medium mb-2">
                <BilingualBlock
                  en={labels.en.studyFindings}
                  zh={labels.zh.studyFindings}
                  mode={languageMode}
                />
              </p>
              <ul className="text-xs text-muted-foreground space-y-1">
                {closureData?.study_result?.findings?.map((finding: string, idx: number) => (
                  <li key={idx}>• {finding}</li>
                )) || <li className="text-xs text-muted-foreground">{languageMode === 'chinese' ? labels.zh.noFindings : labels.en.noFindings}</li>}
              </ul>
              <div className="mt-3 flex gap-4">
                <span className="text-xs">
                  <BilingualBlock en={`${labels.en.status}: `} zh={`${labels.zh.status}: `} mode={languageMode} />
                  <strong>{closureData?.study_result?.completion_status || 'N/A'}</strong>
                </span>
                <span className="text-xs">
                  <BilingualBlock en={`${labels.en.time}: `} zh={`${labels.zh.time}: `} mode={languageMode} />
                  <strong>{closureData?.study_result?.time_spent || 'N/A'}</strong>
                </span>
              </div>
            </div>
            <div className="rounded-md bg-muted p-4">
              <p className="text-xs font-medium mb-2">
                <BilingualBlock
                  en={labels.en.decisionHandoff}
                  zh={labels.zh.decisionHandoff}
                  mode={languageMode}
                />
              </p>
              <p className="text-xs text-muted-foreground">
                <BilingualBlock en={`${labels.en.type}: `} zh={`${labels.zh.type}: `} mode={languageMode} />
                {closureData?.decision_handoff?.decision_type || 'N/A'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                <BilingualBlock en={`${labels.en.justification}: `} zh={`${labels.zh.justification}: `} mode={languageMode} />
                {closureData?.decision_handoff?.justification || 'N/A'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                <BilingualBlock en={`${labels.en.confidenceLabel}: `} zh={`${labels.zh.confidenceLabel}: `} mode={languageMode} />
                {((closureData?.decision_handoff?.confidence || 0) * 100).toFixed(0)}%
              </p>
            </div>
          </div>
          <div className="rounded-md border p-3">
            <p className="text-xs text-muted-foreground">{closureData?.closure_summary || (languageMode === 'chinese' ? labels.zh.noClosureSummary : labels.en.noClosureSummary)}</p>
          </div>
        </div>
      </div>

      {/* B4 Evidence Quality Section (only if B4 report) */}
      {isB4 && report?.b4_evidence && (
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">
              <BilingualBlock
                en={labels.en.evidenceQuality}
                zh={labels.zh.evidenceQuality}
                mode={languageMode}
              />
            </h3>
            <span className="inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium bg-primary/10 text-primary">
              {languageMode === 'chinese' ? labels.zh.b4ReportBadge : labels.en.b4ReportBadge}
            </span>
          </div>
          
          {report.b4_evidence.evidence_summary && (
            <div className="space-y-4">
              {/* Quality Assessment */}
              <div className="rounded-md bg-muted p-4">
                <p className="text-sm font-medium mb-2">
                  <BilingualBlock
                    en="Quality Assessment"
                    zh="质量评估"
                    mode={languageMode}
                  />
                </p>
                <p className="text-xs text-muted-foreground">
                  {report.b4_evidence.evidence_summary.quality_assessment || 'N/A'}
                </p>
                {report.b4_evidence.evidence_summary.recommendation && (
                  <p className="text-xs text-muted-foreground mt-2">
                    {report.b4_evidence.evidence_summary.recommendation}
                  </p>
                )}
              </div>

              {/* Strongest/Weakest Evidence */}
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-md border p-3">
                  <p className="text-xs font-medium mb-1">
                    <BilingualBlock
                      en={labels.en.strongestEvidence}
                      zh={labels.zh.strongestEvidence}
                      mode={languageMode}
                    />
                  </p>
                  <p className="text-sm font-semibold text-green-700">
                    {report.b4_evidence.evidence_summary.strongest_evidence?.replace(/_/g, ' ') || 'N/A'}
                  </p>
                </div>
                <div className="rounded-md border p-3">
                  <p className="text-xs font-medium mb-1">
                    <BilingualBlock
                      en={labels.en.weakestEvidence}
                      zh={labels.zh.weakestEvidence}
                      mode={languageMode}
                    />
                  </p>
                  <p className="text-sm font-semibold text-gray-600">
                    {report.b4_evidence.evidence_summary.weakest_evidence?.replace(/_/g, ' ') || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Layer Distribution */}
              <div className="rounded-md border p-4">
                <p className="text-sm font-medium mb-3">
                  <BilingualBlock
                    en={labels.en.evidenceLayerDistribution}
                    zh={labels.zh.evidenceLayerDistribution}
                    mode={languageMode}
                  />
                </p>
                <div className="space-y-2">
                  {report.b4_evidence.evidence_summary.layer_distribution &&
                    Object.entries(report.b4_evidence.evidence_summary.layer_distribution).map(([layer, count]) => (
                      <div key={layer} className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">
                          {layer.replace(/_/g, ' ')}
                        </span>
                        <span className="text-xs font-medium">
                          {count as number} {languageMode === 'chinese' ? labels.zh.layerCount : labels.en.layerCount}
                        </span>
                      </div>
                    ))}
                </div>
              </div>

              {/* Tagged Entities */}
              {report.b4_evidence.evidence_summary.tagged_entities && report.b4_evidence.evidence_summary.tagged_entities.length > 0 && (
                <div className="rounded-md border p-4">
                  <p className="text-sm font-medium mb-3">
                    <BilingualBlock
                      en={labels.en.taggedEntities}
                      zh={labels.zh.taggedEntities}
                      mode={languageMode}
                    />
                  </p>
                  <div className="space-y-2">
                    {report.b4_evidence.evidence_summary.tagged_entities.map((entity: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between rounded-md bg-muted/50 p-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{entity.entity_name}</span>
                          <span className="inline-flex items-center rounded-md border px-1.5 py-0.5 text-[10px]">
                            {entity.entity_type}
                          </span>
                        </div>
                        <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${
                          entity.evidence_layer === 'authoritative_official' ? 'bg-green-100 text-green-700' :
                          entity.evidence_layer === 'expert_maintainer' ? 'bg-blue-100 text-blue-700' :
                          entity.evidence_layer === 'implementation_repository' ? 'bg-indigo-100 text-indigo-700' :
                          entity.evidence_layer === 'community_discourse' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {entity.evidence_layer.replace(/_/g, ' ')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Advanced Inspect Tools (Collapsible) */}
      <div className="rounded-lg border bg-muted/50">
        <button
          onClick={() => setShowInspectTools(!showInspectTools)}
          className="w-full flex items-center justify-between p-4 hover:bg-muted transition-colors"
        >
          <div className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-muted-foreground" />
            <span className="font-medium text-sm">
              <BilingualBlock en={labels.en.inspectTools} zh={labels.zh.inspectTools} mode={languageMode} />
            </span>
            <span className="ml-2 inline-flex items-center rounded-md bg-secondary px-2 py-0.5 text-xs font-medium text-muted-foreground">
              <BilingualBlock en={labels.en.experimental} zh={labels.zh.experimental} mode={languageMode} />
            </span>
          </div>
          {showInspectTools ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
        {showInspectTools && (
          <div className="p-4 pt-0 border-t">
            <p className="text-xs text-muted-foreground mb-4">
              <BilingualBlock en={labels.en.inspectToolsDesc} zh={labels.zh.inspectToolsDesc} mode={languageMode} />
            </p>
            <div className="grid gap-6 md:grid-cols-2">
              {/* Observation Inspect Card */}
              <div className="rounded-lg border bg-card p-6">
                <div className="mb-4 flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  <h3 className="font-semibold">
                    <BilingualBlock en={labels.en.observationInspect} zh={labels.zh.observationInspect} mode={languageMode} />
                  </h3>
                </div>
                <p className="mb-4 text-sm text-muted-foreground">
                  <BilingualBlock en={labels.en.observationInspectDesc} zh={labels.zh.observationInspectDesc} mode={languageMode} />
                </p>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label htmlFor="observation-json" className="text-sm font-medium">
                      <BilingualBlock en={labels.en.feedItemJson} zh={labels.zh.feedItemJson} mode={languageMode} />
                    </label>
                    <textarea
                      id="observation-json"
                      value={observationJson}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setObservationJson(e.target.value)}
                      className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                      placeholder='{"source_id": "...", "title": "..."}'
                    />
                  </div>
                  <button
                    onClick={handleInspectObservation}
                    disabled={isLoadingObservation}
                    className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
                  >
                    {isLoadingObservation ? labels.en.inspecting : labels.en.inspectObservation}
                  </button>

                  {observationError && (
                    <div className="rounded-md border border-red-500 bg-red-50 p-3 text-sm text-red-600">
                      {observationError}
                    </div>
                  )}

                  {observationResult && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center rounded-md border px-2 py-0.5 text-xs">
                          {observationResult.ref.id_scope}
                        </span>
                        <span className="inline-flex items-center rounded-md border px-2 py-0.5 text-xs">
                          {observationResult.ref.stability}
                        </span>
                      </div>
                      <div className="rounded-md bg-muted p-3">
                        <pre className="text-xs overflow-auto max-h-64">
                          {JSON.stringify(observationResult, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Chain Inspect Card */}
              <div className="rounded-lg border bg-card p-6">
                <div className="mb-4 flex items-center gap-2">
                  <Link className="h-5 w-5" />
                  <h3 className="font-semibold">
                    <BilingualBlock en={labels.en.chainInspect} zh={labels.zh.chainInspect} mode={languageMode} />
                  </h3>
                </div>
                <p className="mb-4 text-sm text-muted-foreground">
                  <BilingualBlock en={labels.en.chainInspectDesc} zh={labels.zh.chainInspectDesc} mode={languageMode} />
                </p>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label htmlFor="artifact-id" className="text-sm font-medium">
                      <BilingualBlock en={labels.en.artifactId} zh={labels.zh.artifactId} mode={languageMode} />
                    </label>
                    <input
                      id="artifact-id"
                      value={artifactId}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setArtifactId(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      placeholder="e.g., 00000000-0000-0000-0000-000000000000"
                    />
                  </div>
                  <button
                    onClick={handleInspectChain}
                    disabled={isLoadingChain}
                    className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
                  >
                    {isLoadingChain ? labels.en.inspecting : labels.en.inspectChain}
                  </button>

                  {chainError && (
                    <div className="rounded-md border border-red-500 bg-red-50 p-3 text-sm text-red-600">
                      {chainError}
                    </div>
                  )}

                  {chainResult && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs ${chainResult.completeness.is_complete ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                          {chainResult.completeness.is_complete ? labels.en.complete : labels.en.incomplete}
                        </span>
                        <span className="inline-flex items-center rounded-md border px-2 py-0.5 text-xs">
                          {chainResult.ref.id_scope}
                        </span>
                        <span className="inline-flex items-center rounded-md border px-2 py-0.5 text-xs">
                          {chainResult.ref.stability}
                        </span>
                      </div>
                      {chainResult.completeness && (
                        <div className="rounded-md bg-muted p-3">
                          <h4 className="text-sm font-medium mb-2">
                            <BilingualBlock en={labels.en.completeness} zh={labels.zh.completeness} mode={languageMode} />
                          </h4>
                          <div className="text-xs space-y-1">
                            <div>
                              <BilingualBlock en={`${labels.en.objects}: `} zh={`${labels.zh.objects}: `} mode={languageMode} />
                              {chainResult.completeness.object_count}
                            </div>
                            {Object.entries(chainResult.completeness.objects || {}).map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="text-muted-foreground">{key}:</span>
                                <span className={value ? 'text-green-600' : 'text-red-600'}>
                                  {value ? '✓' : '✗'}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      <div className="rounded-md bg-muted p-3">
                        <pre className="text-xs overflow-auto max-h-96">
                          {JSON.stringify(chainResult, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
