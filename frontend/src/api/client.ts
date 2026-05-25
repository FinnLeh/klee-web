import createClient from "openapi-fetch";
import type { paths } from "../types/api";

export const BASE_URL = "http://localhost:8000";

export const apiClient = createClient<paths>({ baseUrl: BASE_URL });