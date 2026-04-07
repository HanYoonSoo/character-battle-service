import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { Link as RouterLink } from "react-router-dom";

import { getBattleHistory } from "../features/battles/battlesApi";
import { BattleResultCard } from "../features/battles/BattleResultCard";
import { getLeaderboard } from "../features/leaderboard/leaderboardApi";
import { LeaderboardTable } from "../features/leaderboard/LeaderboardTable";
import type { Battle, LeaderboardEntry, SessionBootstrapResponse } from "../shared/types/domain";
import { EmptyState } from "../shared/ui/EmptyState";
import { LoadingBlock } from "../shared/ui/LoadingBlock";
import { SectionHeader } from "../shared/ui/SectionHeader";
import { StatusBanner } from "../shared/ui/StatusBanner";
import { SummaryCard } from "../shared/ui/SummaryCard";

type HomePageProps = {
  session: SessionBootstrapResponse;
};

export function HomePage({ session }: HomePageProps) {
  const [history, setHistory] = useState<Battle[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const [historyItems, leaderboardItems] = await Promise.all([
          getBattleHistory(),
          getLeaderboard(),
        ]);
        if (active) {
          setHistory(historyItems.slice(0, 3));
          setLeaderboard(leaderboardItems.slice(0, 5));
          setError(null);
        }
      } catch (caught) {
        if (active) {
          setError(caught instanceof Error ? caught.message : "공개 아레나 데이터를 불러오지 못했습니다.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, []);

  return (
    <Stack spacing={4}>
      <Paper
        sx={{
          overflow: "hidden",
          p: { xs: 2.5, md: 3.25 },
          position: "relative",
          background: (theme) =>
            theme.palette.mode === "dark"
              ? "linear-gradient(180deg, rgba(18, 26, 38, 0.96) 0%, rgba(11, 17, 27, 0.92) 100%)"
              : "linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(247, 249, 254, 0.92) 100%)",
        }}
      >
        <Box
          sx={{
            display: "grid",
            gap: 2.5,
            gridTemplateColumns: { xs: "1fr", xl: "minmax(0, 1.25fr) minmax(320px, 0.85fr)" },
          }}
        >
          <Stack spacing={2.5}>
            <Stack spacing={1.2}>
              <Typography color="primary.light" fontSize="0.82rem" fontWeight={700}>
                공개 아레나
              </Typography>
              <Typography sx={{ fontSize: { xs: "1.9rem", md: "2.6rem" }, fontWeight: 700, lineHeight: 1.16 }}>
                캐릭터를 만들고, 상대를 고르고, 바로 결과를 확인하세요.
              </Typography>
              <Typography color="text.secondary" maxWidth={840}>
                누구나 최대 다섯 개의 캐릭터를 만들 수 있고, 공개된 상대와 바로 대결할 수 있습니다.
                이긴 캐릭터는 순위에 오르고, 지난 결과도 계속 돌아볼 수 있습니다.
              </Typography>
            </Stack>

            <Stack direction={{ xs: "column", sm: "row" }} flexWrap="wrap" gap={1.5}>
              <Button component={RouterLink} to="/characters" size="large" variant="contained">
                캐릭터 만들기
              </Button>
              <Button component={RouterLink} to="/battle" color="inherit" size="large" variant="outlined">
                바로 배틀하기
              </Button>
              <Button component={RouterLink} to="/history" color="inherit" size="large" variant="text">
                기록 보기
              </Button>
            </Stack>

            <Box
              sx={{
                display: "grid",
                gap: 1.5,
                gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
              }}
            >
              <SummaryCard
                accent="blue"
                description={session.isNew ? "처음 들어온 플레이어" : "이전 흐름 그대로 이어서 플레이 중"}
                label="플레이 상태"
                value={session.isNew ? "새로 시작" : "이어서 진행"}
              />
              <SummaryCard
                accent="neutral"
                description="최근 결과와 순위를 누구나 볼 수 있습니다"
                label="기록 공개"
                value="전체 공개"
              />
              <SummaryCard
                accent="orange"
                description="모든 대결은 한 명의 승자로 마무리됩니다"
                label="승리 규칙"
                value="승자 1명"
              />
            </Box>
          </Stack>

          <Paper
            sx={{
              p: { xs: 2.25, md: 2.75 },
              borderRadius: 5,
              background: (theme) =>
                theme.palette.mode === "dark"
                  ? "linear-gradient(180deg, rgba(15, 23, 34, 0.96) 0%, rgba(10, 16, 25, 0.9) 100%)"
                  : "linear-gradient(180deg, rgba(250, 252, 255, 0.98) 0%, rgba(241, 246, 255, 0.94) 100%)",
            }}
            variant="outlined"
          >
            <Stack spacing={2}>
              <Typography color="primary.light" fontSize="0.82rem" fontWeight={700}>
                오늘의 아레나
              </Typography>
              <Stack spacing={1}>
                <Typography sx={{ fontSize: { xs: "1.2rem", md: "1.45rem" }, fontWeight: 700 }}>
                  {leaderboard[0]?.name ? `${leaderboard[0].name}가 현재 선두입니다.` : "첫 번째 챔피언을 기다리는 중입니다."}
                </Typography>
                <Typography color="text.secondary">
                  {history[0]?.winnerCharacterName
                    ? `가장 최근 승자는 ${history[0].winnerCharacterName}입니다.`
                    : "아직 기록된 공개 승리가 없습니다."}
                </Typography>
              </Stack>

              <Stack spacing={1.25}>
                <ArenaHighlights session={session} />
              </Stack>
            </Stack>
          </Paper>
        </Box>
      </Paper>

      {error ? <StatusBanner variant="error" message={error} /> : null}

      <Box
        sx={{
          display: "grid",
          gap: 3,
          gridTemplateColumns: { xs: "1fr", xl: "minmax(0, 1.05fr) minmax(0, 1fr)" },
        }}
      >
        <Paper sx={{ p: { xs: 2.25, md: 2.75 } }}>
          <Stack spacing={2.5}>
            <SectionHeader
              eyebrow="리더보드"
              title="현재 순위"
              description="가장 앞서 나가는 캐릭터를 한눈에 확인할 수 있습니다."
            />
            {loading ? <LoadingBlock message="리더보드를 불러오는 중..." /> : <LeaderboardTable items={leaderboard} />}
          </Stack>
        </Paper>

        <Paper sx={{ p: { xs: 2.25, md: 2.75 } }}>
          <Stack spacing={2.5}>
            <SectionHeader
              eyebrow="최신 배틀"
              title="방금 끝난 대결"
              description="가장 최근에 끝난 배틀 결과를 먼저 보여줍니다."
            />
            {loading ? <LoadingBlock message="배틀 기록을 불러오는 중..." /> : null}
            {!loading && history.length === 0 ? (
              <EmptyState
                description="첫 번째 배틀이 끝나면 이 영역에 최신 결과가 표시됩니다."
                title="아직 완료된 배틀이 없습니다"
              />
            ) : null}
            {history[0] ? <BattleResultCard battle={history[0]} /> : null}
            {history.length > 1 ? (
              <Stack spacing={1.25}>
                {history.slice(1).map((battle) => (
                  <BattleResultCard key={battle.battleId} battle={battle} variant="compact" />
                ))}
              </Stack>
            ) : null}
          </Stack>
        </Paper>
      </Box>
    </Stack>
  );
}

function HomeNote({ label, value }: ArenaPointProps) {
  return (
    <Paper
      sx={{
        p: 1.5,
        borderRadius: 4,
        bgcolor: (theme) => (theme.palette.mode === "dark" ? "rgba(12, 19, 29, 0.72)" : "rgba(255, 255, 255, 0.72)"),
      }}
      variant="outlined"
    >
      <Stack spacing={0.35}>
        <Typography color="text.secondary" fontSize="0.8rem" fontWeight={700}>
          {label}
        </Typography>
        <Typography color="text.primary" variant="body2">
          {value}
        </Typography>
      </Stack>
    </Paper>
  );
}

type ArenaPointProps = {
  label: string;
  value: string;
};

function ArenaHighlights({ session }: { session: SessionBootstrapResponse }) {
  return (
    <Stack spacing={1.25}>
      <HomeNote
        label="입장 상태"
        value={session.isNew ? "처음 들어온 플레이어입니다" : "이어서 플레이 중입니다"}
      />
      <HomeNote
        label="배틀 방식"
        value="대결은 한 번에 한 명의 승자가 정해지는 방식으로 진행됩니다"
      />
      <HomeNote
        label="순위 반영"
        value="승리한 캐릭터는 점수를 얻고, 순위표에 바로 반영됩니다"
      />
    </Stack>
  );
}
