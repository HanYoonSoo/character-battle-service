import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";

import type { Battle } from "../../shared/types/domain";
import { formatDateTime } from "../../shared/utils/formatters";

type BattleResultCardProps = {
  battle: Battle;
  variant?: "featured" | "compact";
};

export function BattleResultCard({
  battle,
  variant = "featured",
}: BattleResultCardProps) {
  const modeLabel = battle.battleMode === "practice" ? "연습 배틀" : "공개 배틀";
  const statusTone = getBattleStatusTone(battle.status);
  const statusLabel = getBattleStatusLabel(battle.status);
  const headline =
    statusTone === "pending"
      ? "승부를 가르는 중입니다"
      : statusTone === "failed"
        ? "이번 대결은 결과를 정리하지 못했습니다"
        : `${battle.winnerCharacterName}이(가) 최종 승리했습니다`;
  const explanation =
    battle.explanation ??
    (statusTone === "pending"
      ? "잠시만 기다리면 이번 대결의 승자가 정리됩니다."
      : "이번 대결은 결과를 확정하지 못했습니다. 잠시 후 다시 시도해 주세요.");

  if (variant === "compact") {
    return (
      <Card
        sx={{
          borderRadius: 5,
          boxShadow: (theme) =>
            theme.palette.mode === "dark"
              ? "0 18px 36px rgba(5, 10, 20, 0.24)"
              : "0 16px 30px rgba(27, 39, 73, 0.08)",
        }}
        variant="outlined"
      >
        <CardContent sx={{ p: 2.25 }}>
          <Stack spacing={1.5}>
            <Stack
              alignItems={{ xs: "flex-start", sm: "center" }}
              direction={{ xs: "column", sm: "row" }}
              justifyContent="space-between"
              spacing={1}
            >
              <Stack direction="row" flexWrap="wrap" gap={0.8}>
                <Chip label={modeLabel} size="small" variant="outlined" />
                <Chip color={statusToneToMuiColor(statusTone)} label={statusLabel} size="small" />
              </Stack>
              <Typography color="text.secondary" fontSize="0.8rem" fontWeight={600}>
                {formatDateTime(battle.createdAt)}
              </Typography>
            </Stack>

            <Stack
              alignItems={{ xs: "flex-start", sm: "center" }}
              direction={{ xs: "column", sm: "row" }}
              justifyContent="space-between"
              spacing={1.25}
            >
              <Stack minWidth={0} spacing={0.4}>
                <Typography sx={{ fontSize: "1.02rem", fontWeight: 700 }} noWrap>
                  {battle.leftCharacter.name}
                  <Box component="span" sx={{ color: "text.secondary", mx: 0.9 }}>
                    vs
                  </Box>
                  {battle.rightCharacter.name}
                </Typography>
                <Typography color="text.secondary" variant="body2">
                  {headline}
                </Typography>
              </Stack>
              <Chip
                color={statusTone === "completed" ? "primary" : statusToneToMuiColor(statusTone)}
                label={battle.winnerCharacterName ? `${battle.winnerCharacterName} 승` : statusLabel}
                sx={{ fontWeight: 700 }}
              />
            </Stack>

            <Typography
              color="text.secondary"
              sx={{
                display: "-webkit-box",
                overflow: "hidden",
                WebkitBoxOrient: "vertical",
                WebkitLineClamp: 2,
              }}
              variant="body2"
            >
              {explanation}
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        borderRadius: { xs: 5, md: 6 },
        boxShadow: (theme) =>
          theme.palette.mode === "dark"
            ? "0 26px 56px rgba(5, 10, 20, 0.28)"
            : "0 24px 48px rgba(27, 39, 73, 0.1)",
        overflow: "hidden",
      }}
      variant="outlined"
    >
      <CardContent sx={{ p: { xs: 2.25, md: 2.75 } }}>
        <Stack spacing={2.5}>
          <Stack
            alignItems={{ xs: "flex-start", md: "center" }}
            direction={{ xs: "column", md: "row" }}
            justifyContent="space-between"
            spacing={1.25}
          >
            <Stack direction="row" flexWrap="wrap" gap={0.9}>
              <Chip label={modeLabel} size="small" variant="outlined" />
              <Chip color={statusToneToMuiColor(statusTone)} label={statusLabel} size="small" />
              <Chip
                color={battle.scoreApplied ? "primary" : "default"}
                label={battle.scoreApplied ? "점수 반영 대상" : "점수 미반영"}
                size="small"
              />
            </Stack>
            <Typography color="text.secondary" fontSize="0.84rem" fontWeight={600}>
              {formatDateTime(battle.createdAt)}
            </Typography>
          </Stack>

          <Paper
            sx={{
              overflow: "hidden",
              p: 0,
              borderRadius: { xs: 4, md: 5 },
            }}
            variant="outlined"
          >
            <Box
              sx={{
                background: resolveBannerGradient(statusTone),
                color: "#ffffff",
                p: { xs: 2, md: 2.4 },
              }}
            >
              <Stack spacing={0.75}>
                <Typography fontSize="0.82rem" fontWeight={700} letterSpacing="0.12em" textTransform="uppercase">
                  Battle Result
                </Typography>
                <Typography sx={{ fontSize: { xs: "1.45rem", md: "1.85rem" }, fontWeight: 800, lineHeight: 1.12 }}>
                  {headline}
                </Typography>
              </Stack>
            </Box>

            <Box sx={{ p: { xs: 2, md: 2.4 } }}>
              <Box
                sx={{
                  display: "grid",
                  gap: 1.25,
                  gridTemplateColumns: { xs: "1fr", md: "minmax(0, 1fr) auto minmax(0, 1fr)" },
                }}
              >
                <BattleSide
                  description={battle.leftCharacter.powerDescription}
                  emphasized={battle.winnerCharacterName === battle.leftCharacter.name}
                  label="왼쪽"
                  name={battle.leftCharacter.name}
                />

                <Stack alignItems="center" justifyContent="center" sx={{ py: { xs: 0.5, md: 0 } }}>
                  <Box
                    sx={{
                      alignItems: "center",
                      bgcolor: (theme) =>
                        theme.palette.mode === "dark"
                          ? alpha(theme.palette.primary.light, 0.14)
                          : alpha(theme.palette.primary.main, 0.08),
                      border: (theme) => `1px solid ${alpha(theme.palette.primary.main, 0.14)}`,
                      borderRadius: "50%",
                      display: "flex",
                      fontSize: { xs: "0.95rem", md: "1.02rem" },
                      fontWeight: 800,
                      height: { xs: 58, md: 72 },
                      justifyContent: "center",
                      letterSpacing: "0.12em",
                      width: { xs: 58, md: 72 },
                    }}
                  >
                    VS
                  </Box>
                </Stack>

                <BattleSide
                  description={battle.rightCharacter.powerDescription}
                  emphasized={battle.winnerCharacterName === battle.rightCharacter.name}
                  label="오른쪽"
                  name={battle.rightCharacter.name}
                />
              </Box>
            </Box>
          </Paper>

          <Paper
            sx={{
              borderRadius: { xs: 4, md: 5 },
              p: { xs: 2, md: 2.4 },
              bgcolor: (theme) =>
                theme.palette.mode === "dark"
                  ? alpha(theme.palette.common.black, 0.18)
                  : alpha(theme.palette.primary.main, 0.025),
            }}
            variant="outlined"
          >
            <Stack spacing={1}>
              <Typography color="text.secondary" fontSize="0.78rem" fontWeight={700} letterSpacing="0.12em" textTransform="uppercase">
                심판 코멘트
              </Typography>
              <Typography color="text.primary">{explanation}</Typography>
            </Stack>
          </Paper>
        </Stack>
      </CardContent>
    </Card>
  );
}

type BattleSideProps = {
  label: string;
  name: string;
  description: string;
  emphasized: boolean;
};

function BattleSide({
  label,
  name,
  description,
  emphasized,
}: BattleSideProps) {
  return (
    <Paper
      sx={{
        borderRadius: 4,
        p: 1.75,
        bgcolor: (theme) =>
          emphasized
            ? theme.palette.mode === "dark"
              ? alpha(theme.palette.primary.light, 0.12)
              : alpha(theme.palette.primary.main, 0.06)
            : theme.palette.mode === "dark"
              ? alpha(theme.palette.common.white, 0.02)
              : alpha(theme.palette.common.white, 0.66),
      }}
      variant="outlined"
    >
      <Stack spacing={0.9}>
        <Stack alignItems="center" direction="row" flexWrap="wrap" gap={0.8}>
          <Typography color="text.secondary" fontSize="0.74rem" fontWeight={700} letterSpacing="0.08em" textTransform="uppercase">
            {label}
          </Typography>
          <Chip
            color={emphasized ? "primary" : "default"}
            label={emphasized ? "승리" : "도전"}
            size="small"
            variant={emphasized ? "filled" : "outlined"}
          />
        </Stack>
        <Typography sx={{ fontSize: { xs: "1.05rem", md: "1.18rem" }, fontWeight: 700 }}>
          {name}
        </Typography>
        <Typography color="text.secondary" variant="body2">
          {description}
        </Typography>
      </Stack>
    </Paper>
  );
}

function getBattleStatusTone(status: string): "pending" | "completed" | "failed" {
  if (status.endsWith("_pending")) {
    return "pending";
  }
  if (status.endsWith("_failed")) {
    return "failed";
  }
  return "completed";
}

function getBattleStatusLabel(status: string): string {
  if (status.endsWith("_pending")) {
    return "결과 확인 중";
  }
  if (status.endsWith("_failed")) {
    return "결과 미확정";
  }
  return "결과 완료";
}

function statusToneToMuiColor(
  tone: "pending" | "completed" | "failed",
): "default" | "primary" | "error" | "warning" {
  if (tone === "completed") {
    return "primary";
  }
  if (tone === "failed") {
    return "error";
  }
  return "warning";
}

function resolveBannerGradient(tone: "pending" | "completed" | "failed"): string {
  if (tone === "pending") {
    return "linear-gradient(135deg, #4c6fff 0%, #7f8cff 100%)";
  }
  if (tone === "failed") {
    return "linear-gradient(135deg, #ef5350 0%, #ff7a66 100%)";
  }
  return "linear-gradient(135deg, #4667ff 0%, #ff7c47 100%)";
}
