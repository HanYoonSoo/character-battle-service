import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";

import type { LeaderboardEntry } from "../../shared/types/domain";
import { formatDateTime } from "../../shared/utils/formatters";

type LeaderboardTableProps = {
  items: LeaderboardEntry[];
};

export function LeaderboardTable({ items }: LeaderboardTableProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  if (items.length === 0) {
    return (
      <Paper sx={{ p: 3, borderRadius: 4 }} variant="outlined">
        <Typography color="text.secondary">아직 기록된 승리가 없습니다.</Typography>
      </Paper>
    );
  }

  if (isMobile) {
    return (
      <Stack spacing={1.5}>
        {items.map((entry, index) => (
          <Paper key={entry.characterId} sx={{ p: 2, borderRadius: 4 }} variant="outlined">
            <Stack spacing={1.25}>
              <Stack alignItems="center" direction="row" justifyContent="space-between" spacing={1}>
                <Stack direction="row" spacing={1} sx={{ minWidth: 0 }}>
                  <Chip label={`#${index + 1}`} size="small" sx={{ fontWeight: 700 }} />
                  <Typography fontWeight={700} noWrap>
                    {entry.name}
                  </Typography>
                </Stack>
                <Typography color="primary.main" fontWeight={700}>
                  {entry.score}점
                </Typography>
              </Stack>
              <Stack alignItems="center" direction="row" justifyContent="space-between" spacing={1}>
                <Typography color="text.secondary" variant="body2">
                  승리 {entry.winCount}회
                </Typography>
                <Typography color="text.secondary" variant="body2">
                  {formatDateTime(entry.lastWinAt)}
                </Typography>
              </Stack>
            </Stack>
          </Paper>
        ))}
      </Stack>
    );
  }

  return (
    <TableContainer component={Paper} sx={{ borderRadius: 4 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>#</TableCell>
            <TableCell>캐릭터</TableCell>
            <TableCell>점수</TableCell>
            <TableCell>승리 수</TableCell>
            <TableCell>최근 승리</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map((entry, index) => (
            <TableRow key={entry.characterId}>
              <TableCell>
                <Chip
                  label={`#${index + 1}`}
                  size="small"
                  sx={{ fontWeight: 700, minWidth: 52 }}
                />
              </TableCell>
              <TableCell>
                <Typography fontWeight={700}>{entry.name}</Typography>
              </TableCell>
              <TableCell>{entry.score}</TableCell>
              <TableCell>{entry.winCount}</TableCell>
              <TableCell>{formatDateTime(entry.lastWinAt)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
