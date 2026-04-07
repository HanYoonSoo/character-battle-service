export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: JsonValue;
};

async function request<T>(input: RequestInfo | URL, init?: RequestOptions): Promise<T> {
  const response = await fetch(input, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
    body: init?.body === undefined ? undefined : JSON.stringify(init.body),
  });

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    const payload = (await safeJson(response)) as { detail?: string } | undefined;
    throw new ApiError(payload?.detail ?? `Request failed with status ${response.status}`, response.status);
  }

  return (await response.json()) as T;
}

async function safeJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

export async function getJson<T>(input: RequestInfo | URL, init?: RequestOptions): Promise<T> {
  return request<T>(input, { ...init, method: "GET" });
}

export async function postJson<T>(
  input: RequestInfo | URL,
  body?: JsonValue,
  init?: RequestOptions,
): Promise<T> {
  return request<T>(input, { ...init, method: "POST", body });
}

export async function patchJson<T>(
  input: RequestInfo | URL,
  body?: JsonValue,
  init?: RequestOptions,
): Promise<T> {
  return request<T>(input, { ...init, method: "PATCH", body });
}

export async function deleteJson(
  input: RequestInfo | URL,
  init?: RequestOptions,
): Promise<void> {
  return request<void>(input, { ...init, method: "DELETE" });
}
