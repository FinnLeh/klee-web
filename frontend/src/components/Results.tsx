import { useState, type ReactNode } from "react"
import type { HaltReason, JobResult, TestCase } from "../api/jobs"
import { useJob } from "../hooks/useJob"

type ResultsProps = {
  jobId: string | null
  submitError: boolean
}

export function Results({ jobId, submitError }: ResultsProps) {
  const { data: job, isError: queryError } = useJob(jobId)

  if (submitError || queryError) return <ConnectionErrorState />
  if (jobId === null) return <EmptyState />
  if (job === undefined) return <LoadingState />

  switch (job.status) {
    case "pending":
      return <PendingState />
    case "running":
      return <RunningState result={job.result ?? null} />
    case "done":
      if (job.result?.compile_error) {
        return <CompileErrorView error={job.result.compile_error} />
      }
      return <DoneView result={job.result!} />
    case "failed":
      return <FailedState result={job.result ?? null} />
  }
}

function CenterBlock({ children }: { children: ReactNode }) {
  return (
    <div className="h-full p-6 flex flex-col items-center justify-center text-center text-slate-600 dark:text-slate-400">
      {children}
    </div>
  )
}

function EmptyState() {
  return <CenterBlock>Click Run to execute KLEE on your code.</CenterBlock>
}

function LoadingState() {
  return <CenterBlock>Loading...</CenterBlock>
}

function ConnectionErrorState() {
  return (
    <CenterBlock>
      Cannot reach the backend. Check that it is running on port 8000.
    </CenterBlock>
  )
}

function PendingState() {
  return <CenterBlock>Job queued, waiting for runner...</CenterBlock>
}

function FailedState({ result }: { result: JobResult | null }) {
  return (
    <div className="h-full overflow-auto p-6">
      <h2 className="text-lg font-semibold text-rose-600 dark:text-rose-400 mb-3">
        Job failed
      </h2>
      {result?.messages && (
        <pre className="text-xs font-mono whitespace-pre-wrap p-3 rounded border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200">
          {result.messages}
        </pre>
      )}
    </div>
  )
}

function RunningState({ result }: { result: JobResult | null }) {
  const hasStats = !!result?.stats && Object.keys(result.stats).length > 0
  return (
    <div className="h-full p-6 flex flex-col items-center justify-center gap-6 text-slate-700 dark:text-slate-300">
      <div className="flex items-center gap-2">
        <Spinner />
        <span>KLEE is exploring paths...</span>
      </div>
      {hasStats && (
        <div className="grid grid-cols-2 gap-3 w-full max-w-sm">
          <StatTile label="Instructions" value={formatCount(result!.stats.Instructions)} />
          <StatTile label="Active states" value={formatCount(result!.stats.NumStates)} />
          <StatTile label="Full branches" value={formatCount(result!.stats.FullBranches)} />
          <StatTile label="Wall time" value={formatWallTime(result!.stats.WallTime)} />
        </div>
      )}
      <div className="text-xs text-slate-500 dark:text-slate-500">
        Test cases will appear when KLEE finishes.
      </div>
    </div>
  )
}

function Spinner() {
  return (
    <div className="w-4 h-4 border-2 border-slate-300 dark:border-slate-600 border-t-[var(--klee-accent)] rounded-full animate-spin" />
  )
}

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="px-3 py-2 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
      <div className="text-lg font-semibold tabular-nums text-slate-900 dark:text-slate-100">
        {value}
      </div>
      <div className="text-xs text-slate-500 dark:text-slate-400">{label}</div>
    </div>
  )
}

function CompileErrorView({ error }: { error: string }) {
  return (
    <div className="h-full overflow-auto p-6">
      <h2 className="text-lg font-semibold text-rose-600 dark:text-rose-400 mb-3">
        Compilation failed
      </h2>
      <pre className="text-xs font-mono whitespace-pre-wrap p-3 rounded border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950 text-rose-800 dark:text-rose-200">
        {error}
      </pre>
    </div>
  )
}

function DoneView({ result }: { result: JobResult }) {
  const [tab, setTab] = useState<"tests" | "stats">("tests")
  return (
    <div className="h-full flex flex-col">
      <TabBar
        tab={tab}
        onTabChange={setTab}
        testCaseCount={result.test_cases.length}
      />
      {result.halt_reason && <HaltBadge reason={result.halt_reason} />}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {tab === "tests" ? (
          <TestCasesPanel testCases={result.test_cases} />
        ) : (
          <StatsPanel stats={result.stats} />
        )}
        {result.messages && <Collapsible title="Messages" content={result.messages} />}
        {result.warnings && <Collapsible title="Warnings" content={result.warnings} />}
      </div>
    </div>
  )
}

function HaltBadge({ reason }: { reason: HaltReason }) {
  const isTimeout = reason === "max_time"
  const label = isTimeout
    ? "Stopped at max time. Some paths may be unexplored."
    : "Explored all paths."
  const color = isTimeout
    ? "bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300"
    : "bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400"
  return (
    <div className={`px-4 py-1.5 text-xs border-b border-slate-200 dark:border-slate-700 ${color}`}>
      {label}
    </div>
  )
}

function TabBar({
  tab,
  onTabChange,
  testCaseCount,
}: {
  tab: "tests" | "stats"
  onTabChange: (t: "tests" | "stats") => void
  testCaseCount: number
}) {
  return (
    <div className="flex border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 shrink-0">
      <TabButton active={tab === "tests"} onClick={() => onTabChange("tests")}>
        Test cases ({testCaseCount})
      </TabButton>
      <TabButton active={tab === "stats"} onClick={() => onTabChange("stats")}>
        Stats
      </TabButton>
    </div>
  )
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-4 py-2 text-sm border-b-2 -mb-px ${
        active
          ? "border-[var(--klee-accent)] text-slate-900 dark:text-slate-100"
          : "border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100"
      }`}
    >
      {children}
    </button>
  )
}

function TestCasesPanel({ testCases }: { testCases: TestCase[] }) {
  if (testCases.length === 0) {
    return <div className="text-sm text-slate-500">No test cases.</div>
  }
  return (
    <div className="space-y-2">
      {testCases.map((tc) => (
        <TestCaseCard key={tc.name} testCase={tc} />
      ))}
    </div>
  )
}

function TestCaseCard({ testCase }: { testCase: TestCase }) {
  return (
    <div className="rounded border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div className="px-3 py-1.5 bg-slate-100 dark:bg-slate-900 text-sm font-mono text-slate-700 dark:text-slate-300">
        {testCase.name}
      </div>
      <div className="px-3 py-2 bg-white dark:bg-slate-950 space-y-0.5">
        {Object.entries(testCase.inputs).map(([name, value]) => (
          <div key={name} className="font-mono text-xs flex gap-2">
            <span className="text-slate-500">{name}</span>
            <span className="text-slate-400">=</span>
            <span className="text-slate-900 dark:text-slate-100">{value}</span>
          </div>
        ))}
      </div>
      {testCase.error && (
        <div className="px-3 py-2 text-xs font-mono whitespace-pre-wrap bg-rose-50 dark:bg-rose-950 text-rose-700 dark:text-rose-300 border-t border-rose-200 dark:border-rose-900">
          {testCase.error}
        </div>
      )}
    </div>
  )
}

function StatsPanel({ stats }: { stats: Record<string, number> }) {
  const entries = Object.entries(stats)
  if (entries.length === 0) {
    return <div className="text-sm text-slate-500">No stats.</div>
  }
  return (
    <div>
      {entries.map(([key, value]) => (
        <div
          key={key}
          className="font-mono text-xs flex justify-between py-1 border-b border-slate-100 dark:border-slate-800"
        >
          <span className="text-slate-600 dark:text-slate-400">{key}</span>
          <span className="tabular-nums text-slate-900 dark:text-slate-100">
            {value.toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  )
}

function Collapsible({ title, content }: { title: string; content: string }) {
  return (
    <details className="rounded border border-slate-200 dark:border-slate-700">
      <summary className="px-3 py-1.5 cursor-pointer text-sm bg-slate-50 dark:bg-slate-900 select-none text-slate-700 dark:text-slate-300">
        {title}
      </summary>
      <pre className="px-3 py-2 text-xs font-mono whitespace-pre-wrap overflow-auto bg-white dark:bg-slate-950 max-h-64 text-slate-800 dark:text-slate-200">
        {content}
      </pre>
    </details>
  )
}

function formatCount(n: number | undefined): string {
  return (n ?? 0).toLocaleString()
}

function formatWallTime(microseconds: number | undefined): string {
  const seconds = (microseconds ?? 0) / 1_000_000
  return `${seconds.toFixed(1)}s`
}
