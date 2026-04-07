import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Container from "@mui/material/Container";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { NavLink, Route, Routes, useLocation } from "react-router-dom";

import { BattlePage } from "../pages/BattlePage";
import { CharactersPage } from "../pages/CharactersPage";
import { HistoryPage } from "../pages/HistoryPage";
import { HomePage } from "../pages/HomePage";
import type { SessionBootstrapResponse } from "../shared/types/domain";
import { useAppColorMode } from "./theme";

type AppRouterProps = {
  session: SessionBootstrapResponse;
};

export function AppRouter({ session }: AppRouterProps) {
  const location = useLocation();
  const { mode, toggleMode } = useAppColorMode();
  const shortVisitorId = session.visitorId.slice(0, 8);
  const guestLabel = `guest_${shortVisitorId}`;

  return (
    <Box sx={{ pb: { xs: 5, md: 8 }, position: "relative" }}>
      <Box
        sx={{
          background: (theme) =>
            theme.palette.mode === "dark"
              ? "radial-gradient(circle, rgba(255, 155, 74, 0.18), transparent 68%)"
              : "radial-gradient(circle, rgba(229, 123, 50, 0.12), transparent 70%)",
          borderRadius: "50%",
          filter: "blur(18px)",
          height: 320,
          pointerEvents: "none",
          position: "absolute",
          right: { xs: -120, md: 32 },
          top: 20,
          width: 320,
          zIndex: 0,
        }}
      />
      <Box
        sx={{
          background: (theme) =>
            theme.palette.mode === "dark"
              ? "radial-gradient(circle, rgba(109, 211, 206, 0.12), transparent 70%)"
              : "radial-gradient(circle, rgba(35, 123, 118, 0.1), transparent 72%)",
          borderRadius: "50%",
          bottom: 120,
          filter: "blur(20px)",
          height: 280,
          left: { xs: -120, md: -20 },
          pointerEvents: "none",
          position: "absolute",
          width: 280,
          zIndex: 0,
        }}
      />
      <AppBar
        color="transparent"
        position="sticky"
        sx={{
          backdropFilter: "blur(18px)",
          borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
          boxShadow: "none",
          zIndex: 2,
        }}
      >
        <Toolbar disableGutters sx={{ py: { xs: 1, md: 1.25 } }}>
          <Container maxWidth="lg" sx={{ px: "0 !important" }}>
            <Stack gap={1.25}>
              <Stack
                alignItems={{ xs: "stretch", md: "center" }}
                direction={{ xs: "column", md: "row" }}
                gap={1.25}
                justifyContent="space-between"
              >
                <Stack alignItems="center" direction="row" gap={1.25}>
                  <Box
                    sx={{
                      bgcolor: "primary.main",
                      borderRadius: 3,
                      boxShadow: "0 8px 20px rgba(66, 99, 235, 0.22)",
                      height: 36,
                      width: 36,
                    }}
                  />
                  <Stack spacing={0.15}>
                    <Typography sx={{ fontSize: { xs: "1rem", md: "1.05rem" }, fontWeight: 700 }}>
                      캐릭터 배틀 아레나
                    </Typography>
                    <Typography color="text.secondary" variant="body2">
                      공개 캐릭터를 만들고 바로 대결하는 플레이그라운드
                    </Typography>
                  </Stack>
                </Stack>

                <Stack
                  alignItems={{ xs: "stretch", sm: "center" }}
                  direction={{ xs: "column", sm: "row" }}
                  gap={1}
                >
                  <Chip label={session.isNew ? "새 플레이" : "이어서 플레이"} size="small" />
                  <Paper
                    sx={{
                      alignItems: "center",
                      borderRadius: 999,
                      display: "flex",
                      px: 1.25,
                      py: 0.75,
                    }}
                    variant="outlined"
                  >
                    <Typography fontFamily='"IBM Plex Mono", monospace' fontSize="0.86rem" fontWeight={600}>
                      {guestLabel}
                    </Typography>
                  </Paper>
                  <Button color="inherit" type="button" variant="outlined" onClick={toggleMode}>
                    {mode === "dark" ? "라이트" : "다크"}
                  </Button>
                </Stack>
              </Stack>

              <Box
                sx={{
                  overflowX: "auto",
                  pb: 0.25,
                  "&::-webkit-scrollbar": {
                    display: "none",
                  },
                  scrollbarWidth: "none",
                }}
              >
                <Stack direction="row" gap={1} sx={{ minWidth: "max-content" }}>
                  <NavPill currentPath={location.pathname} targetPath="/" label="홈" />
                  <NavPill currentPath={location.pathname} targetPath="/characters" label="캐릭터" />
                  <NavPill currentPath={location.pathname} targetPath="/battle" label="배틀" />
                  <NavPill currentPath={location.pathname} targetPath="/history" label="기록" />
                </Stack>
              </Box>
            </Stack>
          </Container>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ pt: { xs: 2.5, md: 4 }, position: "relative", zIndex: 1 }}>
        <Box>
          <Routes>
            <Route path="/" element={<HomePage session={session} />} />
            <Route path="/characters" element={<CharactersPage />} />
            <Route path="/battle" element={<BattlePage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </Box>
      </Container>
    </Box>
  );
}

function linkVariant(currentPath: string, targetPath: string) {
  return currentPath === targetPath ? "contained" : "text";
}

type NavPillProps = {
  currentPath: string;
  targetPath: string;
  label: string;
};

function NavPill({ currentPath, targetPath, label }: NavPillProps) {
  return (
    <Button
      component={NavLink}
      to={targetPath}
      sx={{
        borderRadius: 999,
        minWidth: 92,
        px: 2,
        whiteSpace: "nowrap",
      }}
      variant={linkVariant(currentPath, targetPath)}
    >
      {label}
    </Button>
  );
}
