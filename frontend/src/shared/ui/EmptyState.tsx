import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

type EmptyStateProps = {
  title: string;
  description?: string;
};

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <Paper
      sx={{
        p: { xs: 2.25, md: 2.75 },
        borderRadius: 5,
        textAlign: "center",
      }}
      variant="outlined"
    >
      <Stack spacing={1}>
        <Typography sx={{ fontSize: { xs: "1.05rem", md: "1.15rem" }, fontWeight: 700 }}>
          {title}
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
