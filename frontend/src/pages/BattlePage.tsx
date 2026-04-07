import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";
import { useEffect, useRef, useState } from "react";
import { Link as RouterLink } from "react-router-dom";

import {
  createPracticeBattle,
  createRankedRandomBattle,
  getBattleById,
  getBattleHistory,
  getMyPracticeBattleHistory,
} from "../features/battles/battlesApi";
import { BattleResultCard } from "../features/battles/BattleResultCard";
import { getMyCharacters } from "../features/characters/charactersApi";
import type { Battle, Character } from "../shared/types/domain";
import { EmptyState } from "../shared/ui/EmptyState";
import { LoadingBlock } from "../shared/ui/LoadingBlock";
import { PageHero } from "../shared/ui/PageHero";
import { SectionHeader } from "../shared/ui/SectionHeader";
import { StatusBanner } from "../shared/ui/StatusBanner";

const POLL_INTERVAL_MS = 2_000;

type BattleMode = "practice" | "ranked";

export function BattlePage() {
  const [activeMode, setActiveMode] = useState<BattleMode>("practice");
  const [myCharacters, setMyCharacters] = useState<Character[]>([]);
  const [selectedPracticeLeft, setSelectedPracticeLeft] = useState<Character | null>(null);
  const [selectedPracticeRight, setSelectedPracticeRight] = useState<Character | null>(null);
  const [latestPracticeBattle, setLatestPracticeBattle] = useState<Battle | null>(null);
  const [latestRankedBattle, setLatestRankedBattle] = useState<Battle | null>(null);
  const [publicHistory, setPublicHistory] = useState<Battle[]>([]);
  const [practiceHistory, setPracticeHistory] = useState<Battle[]>([]);
  const [pendingRankedBattles, setPendingRankedBattles] = useState<Battle[]>([]);
  const [loading, setLoading] = useState(true);
  const [practiceSubmitting, setPracticeSubmitting] = useState(false);
  const [launchingRankedIds, setLaunchingRankedIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const resultPanelRef = useRef<HTMLDivElement | null>(null);
  const pollTimersRef = useRef<Map<string, number>>(new Map());

  const activeLatestBattle = activeMode === "practice" ? latestPracticeBattle : latestRankedBattle;
  const rankedQueueBattles = pendingRankedBattles.filter(
    (battle) => battle.battleId !== latestRankedBattle?.battleId,
  );
  const pendingRankedCharacterIds = new Set(
    pendingRankedBattles.map((battle) => battle.leftCharacter.characterId),
  );

  useEffect(() => {
    void refreshData();

    return () => {
      pollTimersRef.current.forEach((timerId) => window.clearTimeout(timerId));
      pollTimersRef.current.clear();
    };
  }, []);

  async function refreshData(showLoader = true) {
    if (showLoader) {
      setLoading(true);
    }

    try {
      const [mine, rankedBattles, practiceBattles] = await Promise.all([
        getMyCharacters(),
        getBattleHistory(),
        getMyPracticeBattleHistory(),
      ]);
      setMyCharacters(mine);
      setPublicHistory(rankedBattles.slice(0, 4));
      setPracticeHistory(practiceBattles.slice(0, 4));
      setLatestRankedBattle((current) =>
        current && (isPendingStatus(current.status) || isFailedStatus(current.status))
          ? current
          : rankedBattles[0] ?? null,
      );
      setLatestPracticeBattle((current) =>
        current && isPendingStatus(current.status) ? current : practiceBattles[0] ?? null,
      );
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "배틀 화면 데이터를 불러오지 못했습니다.");
    } finally {
      if (showLoader) {
        setLoading(false);
      }
    }
  }

  function focusResultPanel() {
    if (typeof window === "undefined") {
      return;
    }

    if (window.matchMedia("(max-width: 1199px)").matches) {
      window.requestAnimationFrame(() => {
        resultPanelRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    }
  }

  function clearBattlePoll(battleId: string) {
    const timerId = pollTimersRef.current.get(battleId);
    if (timerId !== undefined) {
      window.clearTimeout(timerId);
      pollTimersRef.current.delete(battleId);
    }
  }

  function scheduleBattlePolling(battleId: string, mode: BattleMode) {
    clearBattlePoll(battleId);

    const poll = async () => {
      try {
        const battle = await getBattleById(battleId);

        if (mode === "practice") {
          setLatestPracticeBattle(battle);
          setPracticeHistory((previous) => mergeBattleList(previous, battle).slice(0, 4));
        } else {
          setLatestRankedBattle(battle);
          setPendingRankedBattles((previous) =>
            isPendingStatus(battle.status)
              ? mergeBattleList(previous, battle)
              : previous.filter((item) => item.battleId !== battle.battleId),
          );
        }

        if (isPendingStatus(battle.status)) {
          const timerId = window.setTimeout(poll, POLL_INTERVAL_MS);
          pollTimersRef.current.set(battleId, timerId);
          return;
        }

        clearBattlePoll(battleId);
        await refreshData(false);
      } catch (caught) {
        clearBattlePoll(battleId);
        setError(caught instanceof Error ? caught.message : "배틀 상태를 불러오지 못했습니다.");
      }
    };

    const timerId = window.setTimeout(poll, POLL_INTERVAL_MS);
    pollTimersRef.current.set(battleId, timerId);
  }

  async function handlePracticeBattle() {
    if (!selectedPracticeLeft || !selectedPracticeRight) {
      setError("연습 배틀은 내 캐릭터 두 명을 선택해야 합니다.");
      return;
    }

    setPracticeSubmitting(true);
    setActiveMode("practice");
    try {
      const battle = await createPracticeBattle({
        leftCharacterId: selectedPracticeLeft.id,
        rightCharacterId: selectedPracticeRight.id,
      });
      setLatestPracticeBattle(battle);
      setPracticeHistory((previous) => mergeBattleList(previous, battle).slice(0, 4));
      setSelectedPracticeLeft(null);
      setSelectedPracticeRight(null);
      setError(null);
      scheduleBattlePolling(battle.battleId, "practice");
      focusResultPanel();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "연습 배틀을 실행하지 못했습니다.");
    } finally {
      setPracticeSubmitting(false);
    }
  }

  async function handleRankedBattle(character: Character) {
    setActiveMode("ranked");
    setLaunchingRankedIds((previous) =>
      previous.includes(character.id) ? previous : [...previous, character.id],
    );

    try {
      const battle = await createRankedRandomBattle({
        myCharacterId: character.id,
      });
      setLatestRankedBattle(battle);
      setPendingRankedBattles((previous) => mergeBattleList(previous, battle));
      setError(null);
      scheduleBattlePolling(battle.battleId, "ranked");
      focusResultPanel();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "공개 배틀을 실행하지 못했습니다.");
    } finally {
      setLaunchingRankedIds((previous) => previous.filter((id) => id !== character.id));
    }
  }

  function handleSelectPracticeLeft(character: Character) {
    setSelectedPracticeLeft(character);
    if (selectedPracticeRight?.id === character.id) {
      setSelectedPracticeRight(null);
    }
  }

  function handleSelectPracticeRight(character: Character) {
    setSelectedPracticeRight(character);
    if (selectedPracticeLeft?.id === character.id) {
      setSelectedPracticeLeft(null);
    }
  }

  return (
    <Stack spacing={3.5}>
      <PageHero
        accent="cool"
        chips={["연습 배틀", "공개 배틀", "캐릭터별 도전"]}
        description="연습 배틀은 내 캐릭터끼리 가볍게 조합을 시험해보고, 공개 배틀은 각 캐릭터 카드에서 바로 도전할 수 있습니다."
        eyebrow="배틀 아레나"
        title="캐릭터를 고르고 바로 붙여보는 배틀 아레나"
      />

      {error ? <StatusBanner variant="error" message={error} /> : null}

      <Paper sx={{ p: { xs: 1, md: 1.25 }, borderRadius: { xs: 4, md: 5 } }}>
        <Stack direction={{ xs: "column", md: "row" }} gap={1.25} justifyContent="space-between">
          <Tabs
            value={activeMode}
            variant="scrollable"
            sx={{
              minHeight: 48,
              "& .MuiTabs-indicator": {
                borderRadius: 999,
                height: 3,
              },
            }}
            onChange={(_event, nextValue: BattleMode) => setActiveMode(nextValue)}
          >
            <Tab label="내 캐릭터끼리" sx={{ minHeight: 48 }} value="practice" />
            <Tab label="랜덤 공개 배틀" sx={{ minHeight: 48 }} value="ranked" />
          </Tabs>

          <Stack direction="row" flexWrap="wrap" gap={1}>
            <Chip label={`내 캐릭터 ${myCharacters.length}명`} size="small" variant="outlined" />
            <Chip
              color={activeMode === "practice" ? "default" : "primary"}
              label={activeMode === "practice" ? "점수 미반영" : `대결 대기 ${pendingRankedBattles.length}건`}
              size="small"
            />
          </Stack>
        </Stack>
      </Paper>

      <Box
        sx={{
          display: "grid",
          gap: 3,
          gridTemplateColumns: { xs: "1fr", xl: "minmax(0, 1.08fr) minmax(360px, 0.92fr)" },
        }}
      >
        <Paper sx={{ p: { xs: 2.25, md: 2.75 }, borderRadius: { xs: 5, md: 6 } }}>
          <Stack spacing={2.75}>
            {activeMode === "practice" ? (
              <>
                <SectionHeader
                  eyebrow="연습 모드"
                  title="내 캐릭터 둘을 골라 바로 겨뤄보세요"
                  description="대결을 시작하면 오른쪽 패널에 가장 최신 결과가 먼저 표시됩니다."
                />

                <Box
                  sx={{
                    display: "grid",
                    gap: 1.5,
                    gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
                  }}
                >
                  <BattleSlotCard
                    description={selectedPracticeLeft?.powerDescription ?? "먼저 첫 번째 출전 캐릭터를 골라주세요."}
                    label="왼쪽 슬롯"
                    tone="blue"
                    value={selectedPracticeLeft?.name ?? "선택 대기"}
                  />
                  <BattleActionCard
                    description="두 슬롯을 모두 채우면 바로 대결을 시작할 수 있습니다."
                    disabled={practiceSubmitting || !selectedPracticeLeft || !selectedPracticeRight}
                    loading={practiceSubmitting}
                    scoreNote="결과 바로 확인"
                    title="연습 배틀 시작"
                    onClick={handlePracticeBattle}
                  />
                  <BattleSlotCard
                    description={selectedPracticeRight?.powerDescription ?? "두 번째 출전 캐릭터를 골라주세요."}
                    label="오른쪽 슬롯"
                    tone="orange"
                    value={selectedPracticeRight?.name ?? "선택 대기"}
                  />
                </Box>
              </>
            ) : (
              <>
                <SectionHeader
                  eyebrow="공개 모드"
                  title="공개 배틀은 캐릭터 카드마다 바로 시작할 수 있습니다"
                  description="한 캐릭터가 판정 대기 중이어도 다른 캐릭터로 추가 공개 배틀을 시작할 수 있습니다. 상대는 자동으로 랜덤 배정됩니다."
                />

                <Box
                  sx={{
                    display: "grid",
                    gap: 1.5,
                    gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
                  }}
                >
                  <BattleSlotCard
                    description="아래 캐릭터 카드에서 바로 공개 배틀을 시작하세요."
                    label="시작 방식"
                    tone="blue"
                    value="카드에서 바로 시작"
                  />
                  <BattleInfoCard
                    description="여러 캐릭터로 공개 배틀에 도전해도 각각 따로 결과가 정리됩니다."
                    label="진행 현황"
                    value={`${pendingRankedBattles.length}건 대기 중`}
                  />
                  <BattleSlotCard
                    description="상대는 다른 사용자의 공개 캐릭터 중 랜덤으로 정해집니다."
                    label="상대 배정"
                    tone="orange"
                    value={latestRankedBattle?.rightCharacter.name ?? "랜덤 자동 배정"}
                  />
                </Box>
              </>
            )}
          </Stack>
        </Paper>

        <Box ref={resultPanelRef} sx={{ alignSelf: "start" }}>
          <Paper
            sx={{
              p: { xs: 2.25, md: 2.75 },
              borderRadius: { xs: 5, md: 6 },
              position: { xl: "sticky" },
              top: { xl: 104 },
            }}
          >
            <Stack spacing={2.25}>
              <SectionHeader
                eyebrow={activeMode === "practice" ? "현재 판정" : "현재 공개 배틀"}
                title={activeMode === "practice" ? "연습 배틀 결과 추적" : "공개 배틀 결과 추적"}
                description={
                  activeMode === "practice"
                    ? "가장 최근에 시작한 연습 배틀이 먼저 표시됩니다."
                    : "가장 최근에 시작한 공개 배틀을 크게 보여주고, 다른 대결은 아래에 함께 표시합니다."
                }
              />

              {activeLatestBattle ? (
                <BattleResultCard battle={activeLatestBattle} />
              ) : (
                <BattleResultPreview
                  description={
                    activeMode === "practice"
                      ? "연습 배틀을 시작하면 이곳에 승자와 코멘트가 표시됩니다."
                      : "공개 배틀을 시작하면 이곳에 가장 먼저 결과가 표시됩니다."
                  }
                  title={
                    activeMode === "practice"
                      ? "아직 연습 배틀이 시작되지 않았습니다"
                      : "아직 공개 배틀이 시작되지 않았습니다"
                  }
                />
              )}

              {activeMode === "ranked" && rankedQueueBattles.length > 0 ? (
                <Stack spacing={1.2}>
                  <Typography color="text.secondary" fontSize="0.8rem" fontWeight={700}>
                    함께 확인할 공개 배틀
                  </Typography>
                  <Stack spacing={1.1}>
                    {rankedQueueBattles.map((battle) => (
                      <BattleResultCard key={battle.battleId} battle={battle} variant="compact" />
                    ))}
                  </Stack>
                </Stack>
              ) : null}
            </Stack>
          </Paper>
        </Box>
      </Box>

      <Paper sx={{ p: { xs: 2.25, md: 2.75 }, borderRadius: { xs: 5, md: 6 } }}>
        <Stack spacing={2.5}>
          <Stack
            alignItems={{ xs: "flex-start", md: "center" }}
            direction={{ xs: "column", md: "row" }}
            justifyContent="space-between"
            spacing={1.25}
          >
            <SectionHeader
              eyebrow={activeMode === "practice" ? "연습용 로스터" : "공개 배틀 출전"}
              title={activeMode === "practice" ? "배틀에 사용할 캐릭터를 고르세요" : "각 캐릭터로 공개 배틀을 바로 시작할 수 있습니다"}
              description={
                activeMode === "practice"
                  ? "같은 캐릭터를 양쪽에 동시에 넣을 수 없습니다."
                  : "결과를 기다리는 캐릭터는 새 대결을 바로 다시 시작할 수 없습니다."
              }
            />

            <Stack direction="row" flexWrap="wrap" gap={1}>
              <Chip
                label={activeMode === "practice" ? "두 슬롯 선택 필요" : "캐릭터별 독립 진행"}
                size="small"
                variant="outlined"
              />
              <Button component={RouterLink} to="/characters" color="inherit" variant="outlined">
                캐릭터 관리
              </Button>
            </Stack>
          </Stack>

          {loading ? <LoadingBlock message="내 캐릭터를 불러오는 중..." /> : null}

          {!loading && activeMode === "practice" && myCharacters.length < 2 ? (
            <EmptyState
              description="연습 배틀을 하려면 내 캐릭터를 두 명 이상 만들어야 합니다."
              title="아직 연습 배틀을 시작할 수 없습니다"
            />
          ) : null}

          {!loading && activeMode === "ranked" && myCharacters.length === 0 ? (
            <EmptyState
              description="공개 배틀을 하려면 먼저 내 캐릭터를 하나 이상 만들어야 합니다."
              title="아직 출전할 캐릭터가 없습니다"
            />
          ) : null}

          <Box
            sx={{
              display: "grid",
              gap: 1.5,
              gridTemplateColumns: {
                xs: "1fr",
                md: "repeat(2, minmax(0, 1fr))",
                xl: "repeat(3, minmax(0, 1fr))",
              },
            }}
          >
            {myCharacters.map((character) => (
              <BattleRosterCard
                key={character.id}
                activeMode={activeMode}
                busy={practiceSubmitting}
                character={character}
                pendingRanked={pendingRankedCharacterIds.has(character.id)}
                rankedLaunching={launchingRankedIds.includes(character.id)}
                selectedLeft={selectedPracticeLeft?.id === character.id}
                selectedRight={selectedPracticeRight?.id === character.id}
                onSelectPracticeLeft={handleSelectPracticeLeft}
                onSelectPracticeRight={handleSelectPracticeRight}
                onStartRankedBattle={handleRankedBattle}
              />
            ))}
          </Box>
        </Stack>
      </Paper>

      <Box
        sx={{
          display: "grid",
          gap: 3,
          gridTemplateColumns: { xs: "1fr", xl: "repeat(2, minmax(0, 1fr))" },
        }}
      >
        <BattleFeedPanel
          battles={practiceHistory}
          description="연습 배틀 결과를 최신순으로 빠르게 다시 볼 수 있습니다."
          emptyDescription="연습 배틀을 한 번 실행하면 이곳에 최근 결과가 차곡차곡 쌓입니다."
          emptyTitle="아직 연습 배틀 기록이 없습니다"
          title="최근 연습 배틀"
        />
        <BattleFeedPanel
          battles={publicHistory}
          description="공개 배틀은 완료된 결과만 공개 기록에 남고, 점수는 승리 시 자동으로 반영됩니다."
          emptyDescription="공개 배틀이 완료되면 이곳에 최근 결과가 표시됩니다."
          emptyTitle="아직 공개 배틀 기록이 없습니다"
          title="최근 공개 배틀"
        />
      </Box>
    </Stack>
  );
}

type BattleSlotCardProps = {
  label: string;
  value: string;
  description: string;
  tone: "blue" | "orange";
};

function BattleSlotCard({
  label,
  value,
  description,
  tone,
}: BattleSlotCardProps) {
  return (
    <Paper
      sx={{
        borderRadius: 4,
        minHeight: 156,
        p: 2,
        background: (theme) =>
          tone === "blue"
            ? theme.palette.mode === "dark"
              ? "linear-gradient(180deg, rgba(18, 28, 42, 0.92) 0%, rgba(12, 18, 27, 0.86) 100%)"
              : "linear-gradient(180deg, rgba(248, 251, 255, 0.98) 0%, rgba(240, 245, 255, 0.94) 100%)"
            : theme.palette.mode === "dark"
              ? "linear-gradient(180deg, rgba(37, 24, 19, 0.9) 0%, rgba(18, 13, 11, 0.84) 100%)"
              : "linear-gradient(180deg, rgba(255, 251, 247, 0.98) 0%, rgba(255, 245, 238, 0.94) 100%)",
      }}
      variant="outlined"
    >
      <Stack justifyContent="space-between" spacing={1.4} sx={{ height: "100%" }}>
        <Typography
          color={tone === "blue" ? "primary.main" : "secondary.main"}
          fontSize="0.78rem"
          fontWeight={700}
          letterSpacing="0.08em"
          textTransform="uppercase"
        >
          {label}
        </Typography>
        <Typography sx={{ fontSize: { xs: "1.3rem", md: "1.5rem" }, fontWeight: 800, lineHeight: 1.16 }}>
          {value}
        </Typography>
        <Typography color="text.secondary" variant="body2">
          {description}
        </Typography>
      </Stack>
    </Paper>
  );
}

type BattleActionCardProps = {
  title: string;
  description: string;
  scoreNote: string;
  disabled: boolean;
  loading: boolean;
  onClick: () => void;
};

function BattleActionCard({
  title,
  description,
  scoreNote,
  disabled,
  loading,
  onClick,
}: BattleActionCardProps) {
  return (
    <Paper
      sx={{
        borderRadius: 4,
        minHeight: 156,
        p: 2,
      }}
      variant="outlined"
    >
      <Stack alignItems="center" justifyContent="space-between" spacing={1.4} sx={{ height: "100%", textAlign: "center" }}>
        <Chip color="primary" label={scoreNote} size="small" />
        <Stack spacing={0.8}>
          <Typography sx={{ fontSize: { xs: "1.15rem", md: "1.28rem" }, fontWeight: 800 }}>
            {title}
          </Typography>
          <Typography color="text.secondary" variant="body2">
            {description}
          </Typography>
        </Stack>
        <Button
          disabled={disabled}
          fullWidth
          size="large"
          variant="contained"
          onClick={onClick}
        >
          {loading ? "대결 준비 중..." : title}
        </Button>
      </Stack>
    </Paper>
  );
}

type BattleInfoCardProps = {
  label: string;
  value: string;
  description: string;
};

function BattleInfoCard({
  label,
  value,
  description,
}: BattleInfoCardProps) {
  return (
    <Paper
      sx={{
        borderRadius: 4,
        minHeight: 156,
        p: 2,
      }}
      variant="outlined"
    >
      <Stack justifyContent="space-between" spacing={1.4} sx={{ height: "100%" }}>
        <Typography color="text.secondary" fontSize="0.78rem" fontWeight={700} letterSpacing="0.08em" textTransform="uppercase">
          {label}
        </Typography>
        <Typography sx={{ fontSize: { xs: "1.3rem", md: "1.5rem" }, fontWeight: 800, lineHeight: 1.16 }}>
          {value}
        </Typography>
        <Typography color="text.secondary" variant="body2">
          {description}
        </Typography>
      </Stack>
    </Paper>
  );
}

type BattleResultPreviewProps = {
  title: string;
  description: string;
};

function BattleResultPreview({
  title,
  description,
}: BattleResultPreviewProps) {
  return (
    <Paper
      sx={{
        borderRadius: { xs: 5, md: 6 },
        p: { xs: 2.5, md: 3 },
        textAlign: "left",
      }}
      variant="outlined"
    >
      <Stack spacing={1.2}>
        <Typography sx={{ fontSize: { xs: "1.1rem", md: "1.22rem" }, fontWeight: 800 }}>
          {title}
        </Typography>
        <Typography color="text.secondary">
          {description}
        </Typography>
      </Stack>
    </Paper>
  );
}

type BattleRosterCardProps = {
  character: Character;
  activeMode: BattleMode;
  selectedLeft: boolean;
  selectedRight: boolean;
  busy: boolean;
  pendingRanked: boolean;
  rankedLaunching: boolean;
  onSelectPracticeLeft: (character: Character) => void;
  onSelectPracticeRight: (character: Character) => void;
  onStartRankedBattle: (character: Character) => void;
};

function BattleRosterCard({
  character,
  activeMode,
  selectedLeft,
  selectedRight,
  busy,
  pendingRanked,
  rankedLaunching,
  onSelectPracticeLeft,
  onSelectPracticeRight,
  onStartRankedBattle,
}: BattleRosterCardProps) {
  const selected = selectedLeft || selectedRight || pendingRanked;

  return (
    <Paper
      sx={{
        borderRadius: 5,
        p: 2,
        borderColor: selected ? "primary.main" : "divider",
        boxShadow: (theme) =>
          selected
            ? `0 0 0 1px ${alpha(theme.palette.primary.main, 0.14)}`
            : "none",
      }}
      variant="outlined"
    >
      <Stack spacing={1.6}>
        <Stack alignItems="center" direction="row" flexWrap="wrap" gap={0.8} justifyContent="space-between">
          <Stack direction="row" flexWrap="wrap" gap={0.8}>
            <Chip
              color={selected ? "primary" : "default"}
              label={selected ? "선택됨" : "사용 가능"}
              size="small"
            />
            {selectedLeft ? <Chip label="왼쪽 슬롯" size="small" variant="outlined" /> : null}
            {selectedRight ? <Chip label="오른쪽 슬롯" size="small" variant="outlined" /> : null}
            {pendingRanked ? <Chip color="warning" label="결과 확인 중" size="small" /> : null}
          </Stack>
        </Stack>

        <Stack spacing={0.8}>
          <Typography sx={{ fontSize: { xs: "1.12rem", md: "1.18rem" }, fontWeight: 800 }}>
            {character.name}
          </Typography>
          <Typography
            color="text.secondary"
            sx={{
              display: "-webkit-box",
              minHeight: 68,
              overflow: "hidden",
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 3,
            }}
            variant="body2"
          >
            {character.powerDescription}
          </Typography>
        </Stack>

        {activeMode === "practice" ? (
          <Stack direction="row" gap={1}>
            <Button
              disabled={busy || selectedRight}
              fullWidth
              variant={selectedLeft ? "contained" : "outlined"}
              onClick={() => onSelectPracticeLeft(character)}
            >
              왼쪽에 배치
            </Button>
            <Button
              color="inherit"
              disabled={busy || selectedLeft}
              fullWidth
              variant={selectedRight ? "contained" : "outlined"}
              onClick={() => onSelectPracticeRight(character)}
            >
              오른쪽에 배치
            </Button>
          </Stack>
        ) : (
          <Button
            disabled={pendingRanked || rankedLaunching}
            fullWidth
            variant="contained"
            onClick={() => onStartRankedBattle(character)}
          >
            {rankedLaunching ? "대결 준비 중..." : pendingRanked ? "결과 확인 중..." : "이 캐릭터로 공개 배틀"}
          </Button>
        )}
      </Stack>
    </Paper>
  );
}

type BattleFeedPanelProps = {
  title: string;
  description: string;
  battles: Battle[];
  emptyTitle: string;
  emptyDescription: string;
};

function BattleFeedPanel({
  title,
  description,
  battles,
  emptyTitle,
  emptyDescription,
}: BattleFeedPanelProps) {
  return (
    <Paper sx={{ p: { xs: 2.25, md: 2.75 }, borderRadius: { xs: 5, md: 6 } }}>
      <Stack spacing={2.25}>
        <SectionHeader description={description} title={title} />
        {battles.length === 0 ? (
          <EmptyState description={emptyDescription} title={emptyTitle} />
        ) : (
          <Stack spacing={1.25}>
            {battles.map((battle) => (
              <BattleResultCard key={battle.battleId} battle={battle} variant="compact" />
            ))}
          </Stack>
        )}
      </Stack>
    </Paper>
  );
}

function mergeBattleList(current: Battle[], nextBattle: Battle): Battle[] {
  return [nextBattle, ...current.filter((battle) => battle.battleId !== nextBattle.battleId)].sort(
    (left, right) => Date.parse(right.createdAt) - Date.parse(left.createdAt),
  );
}

function isPendingStatus(status: string): boolean {
  return status.endsWith("_pending");
}

function isFailedStatus(status: string): boolean {
  return status.endsWith("_failed");
}
