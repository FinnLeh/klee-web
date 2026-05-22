import { useQuery } from "@tanstack/react-query";
import { getJob, type Job } from "../api/jobs";

const POLL_INTERVAL_MS = 1000;

export function useJob(jobId: string | null) {
  return useQuery<Job>({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId!),
    enabled: jobId !== null,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "done" || status === "failed") return false;
      return POLL_INTERVAL_MS;
    },
  });
}