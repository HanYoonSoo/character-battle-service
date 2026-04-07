import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

type PageHeroProps = {
  eyebrow: string;
  title: string;
  description: string;
  chips?: string[];
  accent?: "warm" | "cool";
};

export function PageHero({
  eyebrow,
  title,
  description,
  chips = [],
  accent = "warm",
}: PageHeroProps) {
  return (
    <Paper
      sx={{
        overflow: "hidden",
        p: { xs: 2.25, md: 2.75 },
        position: "relative",
        background: (theme) =>
          accent === "cool"
            ? theme.palette.mode === "dark"
              ? "linear-gradient(180deg, rgba(17, 25, 35, 0.92) 0%, rgba(11, 17, 27, 0.88) 100%)"
              : "linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(244, 248, 255, 0.92) 100%)"
            : theme.palette.mode === "dark"
              ? "linear-gradient(180deg, rgba(17, 25, 35, 0.92) 0%, rgba(11, 17, 27, 0.88) 100%)"
              : "linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(248, 249, 253, 0.92) 100%)",
      }}
    >
      <Box
        sx={{
          background: accent === "cool" ? "rgba(66, 99, 235, 0.1)" : "rgba(255, 107, 61, 0.1)",
          borderRadius: "50%",
          filter: "blur(18px)",
          height: 140,
          pointerEvents: "none",
          position: "absolute",
          right: -24,
          top: -24,
          width: 140,
        }}
      />

      <Stack spacing={2.5} sx={{ position: "relative" }}>
        <Stack
          alignItems={{ xs: "flex-start", md: "center" }}
          direction={{ xs: "column", md: "row" }}
          gap={1.75}
          justifyContent="space-between"
        >
          <Stack spacing={0.9}>
            <Chip
              label={eyebrow}
              size="small"
              sx={{
                alignSelf: "flex-start",
                bgcolor: (theme) =>
                  accent === "cool"
                    ? theme.palette.mode === "dark"
                      ? "rgba(143, 163, 255, 0.12)"
                      : "rgba(66, 99, 235, 0.08)"
                    : theme.palette.mode === "dark"
                      ? "rgba(255, 157, 128, 0.12)"
                      : "rgba(255, 107, 61, 0.08)",
                color: accent === "cool" ? "primary.main" : "secondary.main",
                fontWeight: 700,
              }}
            />
            <Typography sx={{ fontSize: { xs: "1.5rem", md: "1.9rem" }, fontWeight: 700, lineHeight: 1.2 }}>
              {title}
            </Typography>
            <Typography color="text.secondary" maxWidth={820}>
              {description}
            </Typography>
          </Stack>

          {chips.length > 0 ? (
            <Stack direction="row" flexWrap="wrap" gap={1.25} justifyContent={{ xs: "flex-start", md: "flex-end" }}>
              {chips.map((chip) => (
                <Chip key={chip} label={chip} size="small" variant="outlined" />
              ))}
            </Stack>
          ) : null}
        </Stack>
      </Stack>
    </Paper>
  );
}
