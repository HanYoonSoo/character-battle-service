import CircularProgress from "@mui/material/CircularProgress";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

type LoadingBlockProps = {
  message?: string;
};

export function LoadingBlock({ message = "불러오는 중..." }: LoadingBlockProps) {
  return (
    <Paper
      sx={{
        p: { xs: 2.25, md: 2.75 },
        borderRadius: 5,
        background: (theme) =>
          theme.palette.mode === "dark"
            ? "linear-gradient(135deg, rgba(18, 26, 38, 0.9) 0%, rgba(11, 17, 27, 0.82) 100%)"
            : "linear-gradient(135deg, rgba(255, 255, 255, 0.96) 0%, rgba(247, 249, 254, 0.92) 100%)",
      }}
      variant="outlined"
    >
      <Stack alignItems="center" direction="row" spacing={2}>
        <CircularProgress color="primary" size={20} />
        <Typography color="text.secondary" fontWeight={600}>
          {message}
        </Typography>
      </Stack>
    </Paper>
  );
}
