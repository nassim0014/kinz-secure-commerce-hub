/** Tiny fetch helper used by the dashboard. */
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${path}`);
  return res.json() as Promise<T>;
}

export function formatTND(n: number): string {
  return `${n.toLocaleString('en-TN', { maximumFractionDigits: 0 })} TND`;
}
