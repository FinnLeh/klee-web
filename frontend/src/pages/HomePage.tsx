import { StatusBar } from "../components/StatusBar"
import { Workspace } from "../components/Workspace"

export function HomePage() {
  return (
    <Workspace
      topBar={
        <div className="p-2 border-b border-zinc-200 dark:border-zinc-800 bg-zinc-100 dark:bg-zinc-900">
          top bar
        </div>
      }
      main={<div className="p-4 h-full">editor slot</div>}
      results={
        <div className="p-4 h-full bg-zinc-100 dark:bg-zinc-900">
          results slot
        </div>
      }
      statusBar={<StatusBar source="" />}
    />
  )
}
