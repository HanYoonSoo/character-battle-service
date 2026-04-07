import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useState, type ReactNode } from "react";

import { ApiError } from "../../shared/api/http";
import type { SessionBootstrapResponse } from "../../shared/types/domain";
import { LoadingBlock } from "../../shared/ui/LoadingBlock";
import { bootstrapSession } from "./sessionApi";

type SessionGateProps = {
  children: (session: SessionBootstrapResponse) => ReactNode;
};

export function SessionGate({ children }: SessionGateProps) {
  const [session, setSession] = useState<SessionBootstrapResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function run() {
      try {
        const payload = await bootstrapSession();
        if (active) {
          setSession(payload);
          setError(null);
        }
      } catch (caught) {
        const message =
          caught instanceof ApiError ? caught.message : "페이지를 준비하지 못했습니다.";
        if (active) {
          setError(message);
        }
      }
    }

    void run();
    return () => {
      active = false;
    };
  }, []);

  if (error) {
    return (
      <Box
        sx={{
          display: "grid",
          minHeight: "100vh",
          placeItems: "center",
          px: 2,
        }}
      >
        <Paper sx={{ maxWidth: 640, p: { xs: 3, md: 4 }, width: "100%" }}>
          <Stack spacing={2}>
            <Typography color="primary.light" fontSize="0.74rem" letterSpacing="0.16em" textTransform="uppercase">
              준비 오류
            </Typography>
            <Typography variant="h3">페이지를 불러오지 못했습니다</Typography>
            <Alert severity="error">{error}</Alert>
          </Stack>
        </Paper>
      </Box>
    );
  }

  if (!session) {
    return (
      <Box
        sx={{
          display: "grid",
          minHeight: "100vh",
          placeItems: "center",
          px: 2,
        }}
        >
        <Box sx={{ maxWidth: 560, width: "100%" }}>
          <LoadingBlock message="페이지를 준비하는 중..." />
        </Box>
      </Box>
    );
  }

  return <>{children(session)}</>;
}
