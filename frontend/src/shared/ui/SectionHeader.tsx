import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

type SectionHeaderProps = {
  eyebrow?: string;
  title: string;
  description?: string;
};

export function SectionHeader({ eyebrow, title, description }: SectionHeaderProps) {
  return (
    <Stack spacing={1.1}>
      <Stack alignItems="center" direction="row" spacing={1.25}>
        <Box
          sx={{
            bgcolor: "primary.main",
            borderRadius: 999,
            height: 5,
            width: 24,
          }}
        />
        {eyebrow ? (
          <Typography
            color="text.secondary"
            fontSize="0.82rem"
            fontWeight={700}
          >
            {eyebrow}
          </Typography>
        ) : null}
      </Stack>
      <Typography sx={{ fontSize: { xs: "1.35rem", md: "1.55rem" }, fontWeight: 700, lineHeight: 1.22 }}>
        {title}
      </Typography>
      {description ? <Typography color="text.secondary">{description}</Typography> : null}
    </Stack>
  );
}
