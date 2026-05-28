import type { components } from "../types/api";
import { apiClient } from "./client";

export type HaltReason = components["schemas"]["HaltReason"];
export type Job = components["schemas"]["Job"];
export type JobCreated = components["schemas"]["JobCreated"];
export type JobRequest = components["schemas"]["JobRequest"];
export type JobResult = components["schemas"]["JobResult"];
export type JobStatus = components["schemas"]["JobStatus"];
export type KleeFlags = components["schemas"]["KleeFlags"];
export type TestCase = components["schemas"]["TestCase"];

export async function submitJob(req: JobRequest): Promise<JobCreated> {
  const { data, error } = await apiClient.POST("/jobs", { body: req });
  if (error) {
    throw new Error(`submitJob failed: ${JSON.stringify(error)}`);
  }
  return data;
}

export async function getJob(jobId: string): Promise<Job> {
  const { data, error } = await apiClient.GET("/jobs/{job_id}", {
    params: { path: { job_id: jobId } },
  });
  if (error) {
    throw new Error(`getJob(${jobId}) failed: ${JSON.stringify(error)}`);
  }
  return data;
}
