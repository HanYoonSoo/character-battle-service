import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";

import {
  createCharacter,
  deleteCharacter,
  getMyCharacters,
  getPublicCharacters,
  updateCharacter,
} from "../features/characters/charactersApi";
import { CharacterCard } from "../features/characters/CharacterCard";
import { CharacterForm } from "../features/characters/CharacterForm";
import type { Character } from "../shared/types/domain";
import { EmptyState } from "../shared/ui/EmptyState";
import { LoadingBlock } from "../shared/ui/LoadingBlock";
import { PageHero } from "../shared/ui/PageHero";
import { SectionHeader } from "../shared/ui/SectionHeader";
import { StatusBanner } from "../shared/ui/StatusBanner";
import { SummaryCard } from "../shared/ui/SummaryCard";

export function CharactersPage() {
  const [myCharacters, setMyCharacters] = useState<Character[]>([]);
  const [publicCharacters, setPublicCharacters] = useState<Character[]>([]);
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    void refreshData();
  }, []);

  async function refreshData() {
    setLoading(true);
    try {
      const [mine, everyone] = await Promise.all([getMyCharacters(), getPublicCharacters()]);
      setMyCharacters(mine);
      setPublicCharacters(everyone);
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "캐릭터 목록을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(values: { name: string; powerDescription: string }) {
    setBusy(true);
    try {
      await createCharacter(values);
      setSuccess("캐릭터를 생성했습니다.");
      setError(null);
      await refreshData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "캐릭터를 생성하지 못했습니다.");
      setSuccess(null);
    } finally {
      setBusy(false);
    }
  }

  async function handleUpdate(values: { name: string; powerDescription: string }) {
    if (!editingCharacter) {
      return;
    }
    setBusy(true);
    try {
      await updateCharacter(editingCharacter.id, values);
      setSuccess("캐릭터를 수정했습니다.");
      setEditingCharacter(null);
      setError(null);
      await refreshData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "캐릭터를 수정하지 못했습니다.");
      setSuccess(null);
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(character: Character) {
    const confirmed = window.confirm(`${character.name} 캐릭터를 삭제할까요? 배틀 기록은 공개 상태로 유지됩니다.`);
    if (!confirmed) {
      return;
    }
    setBusy(true);
    try {
      await deleteCharacter(character.id);
      setSuccess("캐릭터를 삭제했습니다.");
      setError(null);
      if (editingCharacter?.id === character.id) {
        setEditingCharacter(null);
      }
      await refreshData();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "캐릭터를 삭제하지 못했습니다.");
      setSuccess(null);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Stack spacing={4}>
      <PageHero
        accent="warm"
        chips={["최대 5개 캐릭터", "공개 상대와 대결", "필요하면 수정 가능"]}
        description="내 캐릭터를 만들고 다듬은 뒤 공개 아레나에 올리세요. 내 목록과 공개 목록을 같은 화면에서 함께 관리할 수 있습니다."
        eyebrow="캐릭터 스튜디오"
        title="캐릭터를 설계하고 공개 아레나에 투입하세요"
      />

      {error ? <StatusBanner variant="error" message={error} /> : null}
      {success ? <StatusBanner variant="success" message={success} /> : null}

      <Box
        sx={{
          display: "grid",
          gap: 1.5,
          gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
        }}
      >
        <SummaryCard
          accent="blue"
          description="현재 플레이어가 보유한 캐릭터 수"
          label="내 캐릭터"
          value={`${myCharacters.length} / 5`}
        />
        <SummaryCard
          accent="neutral"
          description="지금 대결 가능한 공개 캐릭터 수"
          label="공개 캐릭터"
          value={`${publicCharacters.length}명`}
        />
        <SummaryCard
          accent="orange"
          description={editingCharacter ? `${editingCharacter.name}을 수정하는 중` : "새 캐릭터를 바로 만들 수 있습니다"}
          label="현재 작업"
          value={editingCharacter ? "수정 모드" : "생성 모드"}
        />
      </Box>

      <Box
        sx={{
          display: "grid",
          gap: 3,
          gridTemplateColumns: { xs: "1fr", xl: "minmax(340px, 0.85fr) minmax(0, 1.15fr)" },
        }}
      >
        <Paper sx={{ p: { xs: 2.25, md: 2.75 }, position: { xl: "sticky" }, top: { xl: 112 }, alignSelf: "start" }}>
          <Stack spacing={3}>
            <Stack direction={{ xs: "column", md: "row" }} gap={1.5} justifyContent="space-between">
              <SectionHeader
                eyebrow="생성"
                title={editingCharacter ? "내 캐릭터 수정" : "새 캐릭터 만들기"}
                description="이름과 설명만 입력하면 바로 공개 아레나에 올릴 수 있습니다."
              />
              <Chip
                color="primary"
                label={`활성 캐릭터 ${myCharacters.length}/5`}
                sx={{ alignSelf: { xs: "flex-start", md: "flex-start" } }}
              />
            </Stack>
            <CharacterForm
              mode={editingCharacter ? "edit" : "create"}
              initialValue={editingCharacter}
              busy={busy}
              onCancel={() => setEditingCharacter(null)}
              onSubmit={editingCharacter ? handleUpdate : handleCreate}
            />
          </Stack>
        </Paper>

        <Paper sx={{ p: { xs: 2.25, md: 2.75 } }}>
          <Stack spacing={3}>
            <SectionHeader
              eyebrow="내 캐릭터"
              title="현재 활성 상태"
              description="지금 보유한 캐릭터를 수정하거나 삭제할 수 있습니다."
            />
            {loading ? <LoadingBlock message="내 캐릭터를 불러오는 중..." /> : null}
            {!loading && myCharacters.length === 0 ? (
              <EmptyState
                description="첫 캐릭터를 만들면 이 영역에 내 카드가 표시됩니다."
                title="아직 만든 캐릭터가 없습니다"
              />
            ) : null}
            <Box
              sx={{
                display: "grid",
                gap: 2,
                gridTemplateColumns: { xs: "1fr", md: "repeat(2, minmax(0, 1fr))" },
              }}
            >
              {myCharacters.map((character) => (
                <CharacterCard
                  key={character.id}
                  busy={busy}
                  character={character}
                  onDelete={handleDelete}
                  onEdit={setEditingCharacter}
                />
              ))}
            </Box>
          </Stack>
        </Paper>
      </Box>

      <Paper sx={{ p: { xs: 2.25, md: 2.75 } }}>
        <Stack spacing={3}>
          <SectionHeader
            eyebrow="공개 풀"
            title="배틀 가능한 캐릭터"
            description="여기 있는 캐릭터는 누구나 선택해서 대결할 수 있습니다."
          />
          <Stack alignItems={{ xs: "flex-start", md: "center" }} direction={{ xs: "column", md: "row" }} gap={1.5}>
            <Chip label={`공개 캐릭터 ${publicCharacters.length}명`} variant="outlined" />
            <Typography color="text.secondary" variant="body2">
              공개 목록은 지금 대결 가능한 캐릭터만 보여줍니다.
            </Typography>
          </Stack>
          {loading ? <LoadingBlock message="공개 캐릭터를 불러오는 중..." /> : null}
          {!loading && publicCharacters.length === 0 ? (
            <EmptyState
              description="첫 공개 캐릭터가 등장하면 이 영역에 카드가 표시됩니다."
              title="아직 공개된 캐릭터가 없습니다"
            />
          ) : null}
          <Box
            sx={{
              display: "grid",
              gap: 2,
              gridTemplateColumns: {
                xs: "1fr",
                md: "repeat(2, minmax(0, 1fr))",
                xl: "repeat(3, minmax(0, 1fr))",
              },
            }}
          >
            {publicCharacters.map((character) => (
              <CharacterCard key={character.id} character={character} />
            ))}
          </Box>
        </Stack>
      </Paper>
    </Stack>
  );
}
