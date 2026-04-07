import { getJson, postJson } from "../../shared/api/http";
import type { Battle, BattleListResponse } from "../../shared/types/domain";

type BattlePayload = {
  leftCharacterId: string;
  rightCharacterId: string;
};

type RankedRandomBattlePayload = {
  myCharacterId: string;
};

export async function createPracticeBattle(payload: BattlePayload): Promise<Battle> {
  return postJson<Battle>("/api/battles/practice", payload);
}

export async function createRankedRandomBattle(payload: RankedRandomBattlePayload): Promise<Battle> {
  return postJson<Battle>("/api/battles/ranked-random", payload);
}

export async function getBattleById(battleId: string): Promise<Battle> {
  return getJson<Battle>(`/api/battles/${battleId}`);
}

export async function getBattleHistory(): Promise<Battle[]> {
  const response = await getJson<BattleListResponse>("/api/battles");
  return response.items;
}

export async function getMyPracticeBattleHistory(): Promise<Battle[]> {
  const response = await getJson<BattleListResponse>("/api/battles/practice/mine");
  return response.items;
}
