const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? '';

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, init);

  if (response.status === 204) return undefined as T;

  const data: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const error = data && typeof data === 'object' ? (data as Record<string, unknown>) : {};
    const detail = error.error ?? error.message ?? error.detail;
    throw new Error(typeof detail === 'string' ? detail : `Erro HTTP ${response.status}`);
  }
  return data as T;
}

export function postJSON(value: unknown, headers: Record<string, string> = {}): RequestInit {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(value),
  };
}

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Não foi possível concluir a operação.';
}
