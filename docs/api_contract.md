# API Contract

## Session

### `POST /api/session/bootstrap`

Purpose:

- Create or refresh an anonymous visitor session.

Response shape:

```json
{
  "visitorId": "uuid",
  "isNew": true
}
```

Behavior:

- Sets an `HttpOnly` cookie.
- Does not require login.
- If a valid cookie already exists, refreshes TTL and returns the existing anonymous user id.
- The cookie value is an opaque session token, not the anonymous user id itself.
- Session TTL is fixed at 30 days unless the project rules change.

## Characters

### `POST /api/characters`

Purpose:

- Create a character owned by the current anonymous user.

Request shape:

```json
{
  "name": "눈빛맨",
  "powerDescription": "쳐다보기만 해도 무조건 이긴다."
}
```

Validation rules:

- maximum 5 characters per anonymous user
- `name` length <= 20
- `powerDescription` length <= 255

### `GET /api/characters/me`

Purpose:

- List characters owned by the current anonymous user.

### `GET /api/characters/public`

Purpose:

- List publicly visible characters that can be selected for battle.

### `PATCH /api/characters/{characterId}`

Purpose:

- Update a character owned by the current anonymous user.

### `DELETE /api/characters/{characterId}`

Purpose:

- Soft delete a character owned by the current anonymous user.

Behavior:

- Characters with battle history must remain referentially intact in history.
- Soft-deleted characters should not appear in public selection lists.
- Soft-deleted characters should not appear in character lookup APIs.
- Public battle history should render from stored battle snapshots instead of live character rows.

## Battles

Transport rule:

- battle creation uses normal HTTP request/response
- v1 does not require WebSocket
- v1 does not require SSE because battle status can be polled with ordinary HTTP
- battle creation endpoints return a `pending` battle first, then the frontend polls `GET /api/battles/{battleId}`
- archive and leaderboard freshness can be handled with ordinary refetch or short polling when needed

### `POST /api/battles/practice`

Purpose:

- Run a private practice battle between two characters owned by the current user.

Request shape:

```json
{
  "leftCharacterId": "uuid",
  "rightCharacterId": "uuid"
}
```

Behavior:

- both characters must belong to the current anonymous user
- practice battles must not update public leaderboard scores
- practice battles must not appear in the public battle feed
- returns `202 Accepted` with a `practice_pending` battle record
- the frontend polls until the battle becomes `practice_completed` or `practice_failed`

### `POST /api/battles/ranked-random`

Purpose:

- Run a public ranked battle using one of the current user's characters and a random opponent character owned by another user.

Request shape:

```json
{
  "myCharacterId": "uuid"
}
```

Response shape:

```json
{
  "battleId": "uuid",
  "battleMode": "ranked",
  "scoreApplied": true,
  "leftCharacter": {
    "characterId": "uuid",
    "name": "string",
    "powerDescription": "string"
  },
  "rightCharacter": {
    "characterId": "uuid",
    "name": "string",
    "powerDescription": "string"
  },
  "winnerCharacterId": null,
  "winnerCharacterName": null,
  "explanation": null,
  "status": "ranked_pending",
  "createdAt": "timestamp",
  "winnerRecordedAt": null
}
```

Validation rules:

- practice battle character ids must differ
- both characters must exist
- winner must be exactly one of the submitted characters
- the same character cannot battle itself
- ranked random battles must select an opponent owned by another anonymous user
- public ranked battle results are public after completion
- practice battle results remain separate from the public feed
- GPT-4o output must first satisfy the configured JSON schema
- battle explanation must be returned in Korean
- battle explanation should use a lightly playful, readable tone
- returns `202 Accepted` with a `ranked_pending` battle record
- each of the current user's characters may start its own ranked-random battle independently
- the frontend polls until the battle becomes `ranked_completed` or `ranked_failed`

### `GET /api/battles/{battleId}`

Purpose:

- Fetch the latest status of a stored battle result.

### `GET /api/battles`

Purpose:

- Fetch the latest public ranked battle records.

Default ordering:

- latest first

### `GET /api/battles/practice/mine`

Purpose:

- Fetch the latest private practice battles created by the current anonymous user.

### `GET /api/leaderboard`

Purpose:

- Fetch public character ranking derived from verified battle scores.

Behavior:

- ranking is served from Redis ZSET
- Redis is not the source of truth and the ranking must be rebuildable from PostgreSQL
- every verified win adds `+1`
- tie-break for equal scores uses recent victory timestamp in ascending order

Response shape:

```json
{
  "items": [
    {
      "characterId": "uuid",
      "name": "string",
      "score": 3,
      "winCount": 3,
      "lastWinAt": "timestamp"
    }
  ]
}
```
