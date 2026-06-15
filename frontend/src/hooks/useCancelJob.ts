import { useMutation } from "@tanstack/react-query";
import { cancelJob } from "../api/jobs";

export function useCancelJob() {
  return useMutation({ mutationFn: cancelJob });
}
