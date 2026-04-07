import { postJson } from "../../shared/api/http";
import type { SessionBootstrapResponse } from "../../shared/types/domain";

export async function bootstrapSession(): Promise<SessionBootstrapResponse> {
  return postJson<SessionBootstrapResponse>("/api/session/bootstrap");
}
