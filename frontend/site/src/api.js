const BASE = import.meta.env.VITE_API_BASE || '';

export async function api(path) {
  const r = await fetch(BASE + path, { credentials: 'include' });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}
