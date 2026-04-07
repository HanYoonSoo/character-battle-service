import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import { useEffect, useState } from "react";

import { getBattleHistory } from "../features/battles/battlesApi";
import { BattleResultCard } from "../features/battles/BattleResultCard";
import { getLeaderboard } from "../features/leaderboard/leaderboardApi";
import { LeaderboardTable } from "../features/leaderboard/LeaderboardTable";
import type { Battle, LeaderboardEntry } from "../shared/types/domain";
import { EmptyState } from "../shared/ui/EmptyState";
import { LoadingBlock } from "../shared/ui/LoadingBlock";
import { PageHero } from "../shared/ui/PageHero";
import { SectionHeader } from "../shared/ui/SectionHeader";
import { StatusBanner } from "../shared/ui/StatusBanner";
import { SummaryCard } from "../shared/ui/SummaryCard";

export function HistoryPage() {
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
          setHistory(historyItems);
          setLeaderboard(leaderboardItems);
          setError(null);
        }
      } catch (caught) {
        if (active) {
          setError(caught instanceof Error ? caught.message : "공개 기록을 불러오지 못했습니다.");
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
      <PageHero
        accent="cool"
        chips={["공개 순위", "최신 결과 우선", "전체 기록 확인"]}
        description="공개 리더보드와 배틀 기록을 한 번에 확인할 수 있습니다. 어떤 캐릭터가 치고 올라오는지 흐름을 바로 파악할 수 있습니다."
        eyebrow="공개 아카이브"
        title="승리 흐름과 챔피언 변화를 한 화면에서 추적하세요"
      />

      {error ? <StatusBanner variant="error" message={error} /> : null}

      <Box
        sx={{
          display: "grid",
          gap: 1.5,
          gridTemplateColumns: { xs: "1fr", md: "repeat(3, minmax(0, 1fr))" },
        }}
      >
        <SummaryCard
          accent="blue"
          description="지금까지 공개된 전체 배틀 수"
          label="공개 배틀"
          value={`${history.length}건`}
        />
        <SummaryCard
          accent="neutral"
          description="리더보드에 이름이 올라간 캐릭터 수"
          label="랭킹 등록"
          value={`${leaderboard.length}명`}
        />
        <SummaryCard
          accent="orange"
          description={leaderboard[0]?.name ? `${leaderboard[0].name}이(가) 가장 앞서 있습니다` : "첫 챔피언을 기다리는 중입니다"}
          label="현재 선두"
          value={leaderboard[0]?.name ?? "대기 중"}
        />
      </Box>

      <Paper sx={{ p: { xs: 2.25, md: 2.75 } }}>
        <Stack spacing={3}>
          <SectionHeader
            eyebrow="순위"
            title="공개 리더보드"
            description="지금 가장 앞서 나가는 캐릭터를 한눈에 볼 수 있습니다."
          />
          {loading ? <LoadingBlock message="리더보드를 불러오는 중..." /> : <LeaderboardTable items={leaderboard} />}
        </Stack>
      </Paper>

      <Paper sx={{ p: { xs: 2.25, md: 2.75 } }}>
        <Stack spacing={3}>
          <SectionHeader
            eyebrow="아카이브"
            title="공개 배틀 기록"
            description="최신 결과가 먼저 보입니다. 지난 대결 흐름을 이어서 살펴볼 수 있습니다."
          />
          {loading ? <LoadingBlock message="배틀 기록을 불러오는 중..." /> : null}
          {!loading && history.length === 0 ? (
            <EmptyState
              description="첫 배틀이 끝나면 이 영역에 결과가 쌓이기 시작합니다."
              title="아직 공개된 배틀 기록이 없습니다"
            />
          ) : null}
          {history[0] ? <BattleResultCard battle={history[0]} /> : null}
          {history.length > 1 ? (
            <Box
              sx={{
                display: "grid",
                gap: 1.5,
                gridTemplateColumns: { xs: "1fr", xl: "repeat(2, minmax(0, 1fr))" },
              }}
            >
              {history.slice(1).map((battle) => (
                <BattleResultCard key={battle.battleId} battle={battle} variant="compact" />
              ))}
            </Box>
          ) : null}
        </Stack>
      </Paper>
    </Stack>
  );
}
