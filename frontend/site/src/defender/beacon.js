// Browser-side beacon: posts a tiny JSON ping back to the defender so it
// knows JS executed in a real browser. Naive scrapers don't run JS, so
// absence of this beacon over multiple requests is a strong bot signal.
//
// Also reports mouse / scroll / keyboard activity flags.

const STATE = { mouse: 0, scroll: 0, key: 0 };

if (typeof window !== 'undefined') {
  window.addEventListener('mousemove', () => STATE.mouse++, { passive: true });
  window.addEventListener('scroll', () => STATE.scroll++, { passive: true });
  window.addEventListener('keydown', () => STATE.key++, { passive: true });
}

const BASE = import.meta.env.VITE_API_BASE || '';

export function startBeacon() {
  if (typeof window === 'undefined') return;
  const send = () => {
    fetch(BASE + '/_defender/beacon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        ua: navigator.userAgent,
        ts: Date.now(),
        mouse: STATE.mouse,
        scroll: STATE.scroll,
        key: STATE.key,
        path: location.pathname,
      }),
    }).catch(() => {});
  };
  // First beacon on load, then every 8s.
  setTimeout(send, 800);
  setInterval(send, 8000);
}
