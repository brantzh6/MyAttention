import IKEWorkspaceManager from '@/components/settings/ike-workspace-manager'
import { promises as fs, statSync } from 'fs'
import path from 'path'

export const dynamic = 'force-dynamic'
export const revalidate = 0

const B4_REPORT_FILE = path.join('.runtime', 'benchmarks', 'ike_b4_harness_report.json')
const B3_REPORT_FILE = path.join('.runtime', 'benchmarks', 'ike_b3_harness_report.json')
const CLOSURE_EXAMPLE_FILE = path.join('.runtime', 'benchmarks', 'ike_harness_study_closure_example.json')
const PROCEDURAL_MEMORY_CANDIDATE_FILE = path.join('.runtime', 'benchmarks', 'ike_harness_procedural_memory_candidate.json')

function findBenchmarkRoot(): string | null {
  const candidates: string[] = []
  
  // From process.cwd()
  candidates.push(process.cwd())
  candidates.push(path.dirname(process.cwd()))
  candidates.push(path.dirname(path.dirname(process.cwd())))
  
  // From __dirname
  candidates.push(path.resolve(__dirname, '../../../'))
  candidates.push(path.resolve(__dirname, '../../../../'))
  candidates.push(path.resolve(__dirname, '../../../../../'))
  
  for (const root of candidates) {
    // Try B4 report first
    const b4Path = path.join(root, B4_REPORT_FILE)
    try {
      if (statSync(b4Path).isFile()) {
        return root
      }
    } catch {
      // B4 not found, continue
    }
    
    // Fallback to B3 report
    const b3Path = path.join(root, B3_REPORT_FILE)
    try {
      if (statSync(b3Path).isFile()) {
        return root
      }
    } catch {
      // B3 not found, try next candidate
    }
  }
  
  return null
}

async function loadBenchmarkData() {
  const root = findBenchmarkRoot()
  
  if (!root) {
    return {
      report: null,
      closure: null,
      error: 'Benchmark files not found. Expected .runtime/benchmarks/ike_b4_harness_report.json or ike_b3_harness_report.json',
      isB4: false,
    }
  }
  
  // Try B4 first, fallback to B3
  const b4Path = path.join(root, B4_REPORT_FILE)
  const b3Path = path.join(root, B3_REPORT_FILE)
  const closurePath = path.join(root, CLOSURE_EXAMPLE_FILE)
  
  let reportPath = b4Path
  let isB4 = true
  
  try {
    if (!statSync(b4Path).isFile()) {
      reportPath = b3Path
      isB4 = false
    }
  } catch {
    reportPath = b3Path
    isB4 = false
  }
  
  try {
    const [reportRaw, closureRaw, candidateRaw] = await Promise.all([
      fs.readFile(reportPath, 'utf-8'),
      fs.readFile(closurePath, 'utf-8'),
      fs.readFile(path.join(root, PROCEDURAL_MEMORY_CANDIDATE_FILE), 'utf-8').catch(() => null),
    ])
    return {
      report: JSON.parse(reportRaw),
      closure: JSON.parse(closureRaw),
      proceduralMemoryCandidate: candidateRaw ? JSON.parse(candidateRaw) : null,
      error: null,
      isB4,
    }
  } catch (err: any) {
    return {
      report: null,
      closure: null,
      proceduralMemoryCandidate: null,
      error: err.message || 'Failed to load benchmark data',
      isB4: false,
    }
  }
}

export default async function IKEWorkspacePage() {
  const { report, closure, proceduralMemoryCandidate, error, isB4 } = await loadBenchmarkData()

  return (
    <div className="p-6">
      <IKEWorkspaceManager report={report} closure={closure} proceduralMemoryCandidate={proceduralMemoryCandidate} loadError={error} isB4={isB4} />
    </div>
  )
}
