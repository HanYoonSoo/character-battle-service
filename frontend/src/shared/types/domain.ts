export type SessionBootstrapResponse = {
  visitorId: string;
  isNew: boolean;
};

export type Character = {
  id: string;
  ownerVisitorId: string;
  name: string;
  powerDescription: string;
  createdAt: string;
  updatedAt: string;
};

export type CharacterListResponse = {
  items: Character[];
};

export type BattleParticipant = {
  characterId: string;
  name: string;
  powerDescription: string;
};

export type Battle = {
  battleId: string;
  battleMode: "practice" | "ranked";
  scoreApplied: boolean;
  leftCharacter: BattleParticipant;
  rightCharacter: BattleParticipant;
  winnerCharacterId: string | null;
  winnerCharacterName: string | null;
  explanation: string | null;
  status: string;
  createdAt: string;
  winnerRecordedAt: string | null;
};

export type BattleListResponse = {
  items: Battle[];
};

export type LeaderboardEntry = {
  characterId: string;
  name: string;
  score: number;
  winCount: number;
  lastWinAt: string | null;
};

export type LeaderboardResponse = {
  items: LeaderboardEntry[];
};
