import { StatusBar } from "../components/StatusBar"
import { TopBar } from "../components/TopBar"
import { Workspace } from "../components/Workspace"

export function HomePage() {
  return (
    <Workspace
      topBar={<TopBar onRun={() => {}} onOpenSettings={() => {}} />}
      main={<div className="p-4 h-full">editor slot</div>}
      results={
        <div className="p-4 h-full bg-slate-100 dark:bg-slate-900">
          results slot
        </div>
      }
      statusBar={<StatusBar source="" />}
    />
  )
}
