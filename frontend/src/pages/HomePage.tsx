import { useState } from "react"
import type { KleeFlags } from "../api/jobs"
import { Editor } from "../components/Editor"
import { Results } from "../components/Results"
import { StatusBar } from "../components/StatusBar"
import { TopBar } from "../components/TopBar"
import { Workspace } from "../components/Workspace"
import { useSubmitJob } from "../hooks/useSubmitJob"

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
  const [flags, setFlags] = useState<KleeFlags>({ max_time: 60, max_memory: 512 })
  const [jobId, setJobId] = useState<string | null>(null)
  const [errorsFirst, setErrorsFirst] = useState(false)
  const submitMutation = useSubmitJob()

  const handleRun = () => {
    submitMutation.mutate(
      { source, flags },
      { onSuccess: (data) => setJobId(data.job_id) },
    )
  }

  return (
    <Workspace
      topBar={
        <TopBar
          flags={flags}
          onFlagsChange={setFlags}
          onRun={handleRun}
        />
      }
      main={<Editor value={source} onChange={setSource} />}
      results={
        <Results
          jobId={jobId}
          submitError={submitMutation.isError}
          errorsFirst={errorsFirst}
          onErrorsFirstChange={setErrorsFirst}
        />
      }
      statusBar={<StatusBar source={source} />}
    />
  )
}
