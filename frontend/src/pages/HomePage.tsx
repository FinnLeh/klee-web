import { useState } from "react"
import { Editor } from "../components/Editor"
import { StatusBar } from "../components/StatusBar"
import { TopBar } from "../components/TopBar"
import { Workspace } from "../components/Workspace"

const GET_SIGN_C = `#include <klee/klee.h>

int get_sign(int x) {
  if (x == 0) return 0;
  if (x < 0) return -1;
  return 1;
}

int main() {
  int a;
  klee_make_symbolic(&a, sizeof(a), "a");
  return get_sign(a);
}
`

export function HomePage() {
  const [source, setSource] = useState<string>(GET_SIGN_C)

  return (
    <Workspace
      topBar={<TopBar onRun={() => {}} onOpenSettings={() => {}} />}
      main={<Editor value={source} onChange={setSource} />}
      results={
        <div className="p-4 h-full bg-slate-100 dark:bg-slate-900">
          results slot
        </div>
      }
      statusBar={<StatusBar source={source} />}
    />
  )
}
