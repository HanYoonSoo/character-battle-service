const KOREAN_LOCALE = "ko-KR";

export function formatDate(value: string) {
  return new Date(value).toLocaleDateString(KOREAN_LOCALE);
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "-";
  }

  return new Date(value).toLocaleString(KOREAN_LOCALE);
}
