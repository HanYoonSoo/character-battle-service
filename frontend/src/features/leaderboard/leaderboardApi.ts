import { getJson } from "../../shared/api/http";
import type { LeaderboardEntry, LeaderboardResponse } from "../../shared/types/domain";

export async function getLeaderboard(): Promise<LeaderboardEntry[]> {
  const response = await getJson<LeaderboardResponse>("/api/leaderboard");
  return response.items;
}
