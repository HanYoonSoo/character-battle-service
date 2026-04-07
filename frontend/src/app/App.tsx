import { BrowserRouter } from "react-router-dom";
import Box from "@mui/material/Box";

import { SessionGate } from "../features/session/SessionGate";
import type { SessionBootstrapResponse } from "../shared/types/domain";
import { AppRouter } from "./router";

export function App() {
  return (
    <BrowserRouter>
      <Box sx={{ minHeight: "100vh" }}>
        <SessionGate>{(session: SessionBootstrapResponse) => <AppRouter session={session} />}</SessionGate>
      </Box>
    </BrowserRouter>
  );
}
