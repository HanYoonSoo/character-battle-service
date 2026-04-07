import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import type { Character } from "../../shared/types/domain";
import { formatDate } from "../../shared/utils/formatters";

type CharacterCardProps = {
  character: Character;
  selected?: boolean;
  busy?: boolean;
  onSelect?: (character: Character) => void;
  onEdit?: (character: Character) => void;
  onDelete?: (character: Character) => void;
  actionLabel?: string;
};

export function CharacterCard({
  character,
  selected = false,
  busy = false,
  onSelect,
  onEdit,
  onDelete,
  actionLabel = "선택",
}: CharacterCardProps) {
  return (
    <Card
      sx={{
        borderColor: selected ? "primary.main" : "divider",
        boxShadow: selected ? "0 0 0 1px rgba(66, 99, 235, 0.18)" : undefined,
        overflow: "hidden",
        position: "relative",
        "&::before": {
          background:
            "linear-gradient(90deg, rgba(66, 99, 235, 0.95) 0%, rgba(255, 107, 61, 0.75) 100%)",
          content: '""',
          height: 3,
          left: 0,
          opacity: selected ? 1 : 0.45,
          position: "absolute",
          right: 0,
          top: 0,
        },
      }}
      variant="outlined"
    >
      <CardContent sx={{ pb: 2, position: "relative" }}>
        <Stack spacing={1.75}>
          <Stack direction="row" justifyContent="space-between" spacing={2}>
            <Stack spacing={1.25}>
              <Stack direction="row" flexWrap="wrap" gap={1}>
                <Chip color={selected ? "primary" : "default"} label={selected ? "선택 완료" : "배틀 가능"} size="small" />
                <Chip label="공개 캐릭터" size="small" variant="outlined" />
              </Stack>
              <Stack spacing={0.75}>
                <Typography color="text.secondary" fontSize="0.8rem" fontWeight={700}>
                  캐릭터
                </Typography>
                <Typography sx={{ fontSize: "1.12rem", fontWeight: 700, lineHeight: 1.25 }}>
                  {character.name}
                </Typography>
              </Stack>
            </Stack>

            <Stack alignItems="flex-end" spacing={1.25}>
              <Chip label={formatDate(character.createdAt)} size="small" variant="outlined" />
              <Box sx={{ bgcolor: selected ? "primary.main" : "divider", borderRadius: "50%", height: 8, width: 8 }} />
            </Stack>
          </Stack>

          <Typography
            color="text.secondary"
            sx={{
              display: "-webkit-box",
              overflow: "hidden",
              WebkitBoxOrient: "vertical",
              WebkitLineClamp: 3,
            }}
          >
            {character.powerDescription}
          </Typography>

          <Stack alignItems="center" direction="row" flexWrap="wrap" gap={1}>
            <Chip label="공개 풀" size="small" variant="outlined" />
            <Chip label={onEdit || onDelete ? "내가 만든 캐릭터" : "공개 탐색용"} size="small" variant="outlined" />
          </Stack>
        </Stack>
      </CardContent>

      <CardActions sx={{ flexWrap: "wrap", gap: 1, px: 2, pb: 2.25, pt: 0 }}>
        {onSelect ? (
          <Button
            color="primary"
            disabled={busy}
            sx={{ flex: onEdit || onDelete ? "0 0 auto" : "1 1 180px" }}
            variant="contained"
            onClick={() => onSelect(character)}
          >
            {selected ? "선택됨" : actionLabel}
          </Button>
        ) : null}
        {onEdit ? (
          <Button color="inherit" disabled={busy} sx={{ flex: "1 1 120px" }} variant="outlined" onClick={() => onEdit(character)}>
            수정
          </Button>
        ) : null}
        {onDelete ? (
          <Button
            color="error"
            disabled={busy}
            sx={{ flex: "1 1 120px" }}
            variant="outlined"
            onClick={() => onDelete(character)}
          >
            삭제
          </Button>
        ) : null}
      </CardActions>
    </Card>
  );
}
