import Alert from "@mui/material/Alert";

type StatusBannerProps = {
  variant?: "info" | "error" | "success";
  message: string;
};

export function StatusBanner({ variant = "info", message }: StatusBannerProps) {
  const severity = variant === "error" ? "error" : variant === "success" ? "success" : "info";
  return (
    <Alert
      severity={severity}
      sx={{
        alignItems: "center",
        px: { xs: 1.5, md: 2 },
        py: 1.1,
      }}
      variant="outlined"
    >
      {message}
    </Alert>
  );
}
