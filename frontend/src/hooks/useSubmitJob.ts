import { useMutation } from "@tanstack/react-query";
import { submitJob } from "../api/jobs";

export function useSubmitJob() {
  return useMutation({ mutationFn: submitJob });
}
