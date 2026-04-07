import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

type SummaryCardProps = {
  label: string;
  value: string;
  description?: string;
  accent?: "blue" | "orange" | "neutral";
};

export function SummaryCard({
  label,
  value,
  description,
  accent = "blue",
}: SummaryCardProps) {
  return (
    <Paper
      sx={{
        p: 2.25,
        borderRadius: 5,
        position: "relative",
        overflow: "hidden",
        "&::before": {
          background:
            accent === "orange"
              ? "linear-gradient(90deg, rgba(255, 107, 61, 0.9) 0%, rgba(255, 153, 102, 0.68) 100%)"
              : accent === "neutral"
                ? "linear-gradient(90deg, rgba(120, 134, 161, 0.7) 0%, rgba(178, 188, 204, 0.54) 100%)"
                : "linear-gradient(90deg, rgba(66, 99, 235, 0.92) 0%, rgba(116, 143, 255, 0.66) 100%)",
          content: '""',
          height: 3,
          left: 0,
          position: "absolute",
          right: 0,
          top: 0,
        },
      }}
      variant="outlined"
    >
      <Stack spacing={0.8}>
        <Typography color="text.secondary" fontSize="0.82rem" fontWeight={700}>
          {label}
        </Typography>
        <Typography sx={{ fontSize: { xs: "1.35rem", md: "1.55rem" }, fontWeight: 700, lineHeight: 1.2 }}>
          {value}
        </Typography>
        {description ? (
          <Typography color="text.secondary" variant="body2">
            {description}
          </Typography>
        ) : null}
      </Stack>
    </Paper>
  );
}
