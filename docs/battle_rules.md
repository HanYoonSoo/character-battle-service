# Battle Rules

These rules constrain the battle-judgment workflow.

## Output Contract

- Every battle must return exactly one winner.
- Draws are not allowed.
- The winner must be one of the two submitted characters.
- The explanation must reference the submitted character descriptions.
- The model response must satisfy the backend JSON schema before any domain validation runs.

## Validation Expectations

- Reject outputs that mention a third winner or no winner.
- Reject outputs that are missing the winning character identifier.
- Reject outputs that are not valid JSON when the backend expects structured output.
- Reject outputs that fail JSON schema validation even if they look parseable.

## Prompting Direction

- Give the LLM both character profiles and any global battle rules.
- Instruct it to return structured output only.
- Use GPT-4o with JSON schema-constrained structured output.
- Treat the LLM as a judge, not as a storyteller with unlimited freedom.

## Future Extension

- Add battle-memory retrieval if you want the model to stay consistent with previous judgments.
- Add moderation rules if character descriptions can contain unsafe input.
