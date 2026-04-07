import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useEffect, useState, type FormEvent } from "react";

import type { Character } from "../../shared/types/domain";
import type { CharacterFormValues } from "./types";

type CharacterFormProps = {
  mode: "create" | "edit";
  initialValue?: Character | null;
  busy?: boolean;
  onCancel?: () => void;
  onSubmit: (values: CharacterFormValues) => Promise<void> | void;
};

const EMPTY_FORM: CharacterFormValues = {
  name: "",
  powerDescription: "",
};

export function CharacterForm({
  mode,
  initialValue,
  busy = false,
  onCancel,
  onSubmit,
}: CharacterFormProps) {
  const [values, setValues] = useState<CharacterFormValues>(EMPTY_FORM);

  useEffect(() => {
    if (!initialValue) {
      setValues(EMPTY_FORM);
      return;
    }
    setValues({
      name: initialValue.name,
      powerDescription: initialValue.powerDescription,
    });
  }, [initialValue]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      name: values.name.trim(),
      powerDescription: values.powerDescription.trim(),
    });
    if (mode === "create") {
      setValues(EMPTY_FORM);
    }
  }

  return (
    <Stack component="form" spacing={2} onSubmit={handleSubmit}>
      <Typography color="text.secondary" variant="body2">
        캐릭터 이름은 짧고 선명하게, 설명은 한 줄 개념이 바로 보이게 적는 편이 좋습니다.
      </Typography>

      <Box
        sx={{
          display: "grid",
          gap: 1.25,
          gridTemplateColumns: { xs: "1fr", sm: "minmax(0, 1fr) auto" },
        }}
      >
        <TextField
          fullWidth
          inputProps={{ maxLength: 20 }}
          label="캐릭터 이름"
          placeholder="예: 눈빛맨"
          value={values.name}
          onChange={(event) => setValues((prev) => ({ ...prev, name: event.target.value }))}
        />

        <Button
          color="primary"
          disabled={busy}
          sx={{ minWidth: 112 }}
          type="submit"
          variant="contained"
        >
          {busy ? "저장 중..." : mode === "create" ? "생성" : "저장"}
        </Button>
      </Box>

      <TextField
        fullWidth
        inputProps={{ maxLength: 255 }}
        label="캐릭터 설명"
        minRows={5}
        multiline
        placeholder="예: 쳐다보기만 해도 무조건 이긴다."
        value={values.powerDescription}
        onChange={(event) =>
          setValues((prev) => ({ ...prev, powerDescription: event.target.value }))
        }
      />

      <Paper
        sx={{
          px: 1.5,
          py: 1.25,
          borderRadius: 4,
          bgcolor: "background.paper",
        }}
        variant="outlined"
      >
        <Stack alignItems={{ xs: "flex-start", sm: "center" }} direction={{ xs: "column", sm: "row" }} gap={1.5} justifyContent="space-between">
          <Typography color="text.secondary" fontSize="0.82rem">
            이름은 최대 20자, 설명은 최대 255자까지 입력할 수 있습니다.
          </Typography>
          <Stack color="text.secondary" direction="row" gap={1.5}>
            <Typography fontSize="0.8rem">{values.name.length}/20</Typography>
            <Typography fontSize="0.8rem">{values.powerDescription.length}/255</Typography>
          </Stack>
        </Stack>
      </Paper>

      {mode === "edit" && onCancel ? (
        <Stack direction="row" flexWrap="wrap" gap={1.5}>
          <Button
            color="inherit"
            disabled={busy}
            type="button"
            variant="outlined"
            onClick={onCancel}
          >
            취소
          </Button>
        </Stack>
      ) : null}
    </Stack>
  );
}
