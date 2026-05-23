// Browser-side proof-of-work solver.
// The server hands out a challenge (prefix + difficulty). The client must
// find a nonce such that sha256(prefix + nonce) has `difficulty` leading
// hex zeros. ~50ms for difficulty 4, seconds for difficulty 5+.

async function sha256Hex(str) {
  const buf = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return [...new Uint8Array(hash)]
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export async function solvePoW(prefix, difficulty) {
  const target = '0'.repeat(difficulty);
  for (let n = 0; n < 5_000_000; n++) {
    const h = await sha256Hex(prefix + n);
    if (h.startsWith(target)) return { nonce: n, hash: h };
  }
  throw new Error('PoW unsolved');
}

const BASE = import.meta.env.VITE_API_BASE || '';

export async function fetchAndSolveChallenge() {
  const r = await fetch(BASE + '/_defender/pow/challenge');
  if (!r.ok) return false;
  const { prefix, difficulty } = await r.json();
  const t0 = performance.now();
  const sol = await solvePoW(prefix, difficulty);
  const dt = performance.now() - t0;
  await fetch(BASE + '/_defender/pow/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...sol, prefix, difficulty, solveMs: dt }),
  });
  return true;
}
