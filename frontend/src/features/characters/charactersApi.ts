import { deleteJson, getJson, patchJson, postJson } from "../../shared/api/http";
import type { Character, CharacterListResponse } from "../../shared/types/domain";

type CharacterPayload = {
  name: string;
  powerDescription: string;
};

type CharacterPatchPayload = Partial<CharacterPayload>;

export async function getMyCharacters(): Promise<Character[]> {
  const response = await getJson<CharacterListResponse>("/api/characters/me");
  return response.items;
}

export async function getPublicCharacters(): Promise<Character[]> {
  const response = await getJson<CharacterListResponse>("/api/characters/public");
  return response.items;
}

export async function createCharacter(payload: CharacterPayload): Promise<Character> {
  return postJson<Character>("/api/characters", payload);
}

export async function updateCharacter(
  characterId: string,
  payload: CharacterPatchPayload,
): Promise<Character> {
  return patchJson<Character>(`/api/characters/${characterId}`, payload);
}

export async function deleteCharacter(characterId: string): Promise<void> {
  return deleteJson(`/api/characters/${characterId}`);
}
