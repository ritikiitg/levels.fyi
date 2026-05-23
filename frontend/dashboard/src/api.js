// Direct-to-backend (bypasses the Vite dev proxy, which is buggy on Windows
// for WebSockets). Mirror the page's hostname so localhost↔localhost and
// 127.0.0.1↔127.0.0.1 — avoids cross-origin gotchas on dev.
const DEFAULT_BACKEND =
  typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : 'http://127.0.0.1:8000';
const BASE = import.meta.env.VITE_API_BASE || DEFAULT_BACKEND;

export async function api(path) {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}

export async function apiPost(path) {
  const r = await fetch(BASE + path, { method: 'POST' });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}

export function openLiveFeed(onMessage, onOpen, onClose) {
  const protocol = BASE.startsWith('https') ? 'wss' : 'ws';
  const host = BASE.replace(/^https?:\/\//, '');
  const url = `${protocol}://${host}/_defender/ws`;
  // eslint-disable-next-line no-console
  console.log('[this1] WS connecting to', url);
  let ws;
  let stop = false;

  function connect() {
    try {
      ws = new WebSocket(url);
    } catch (e) {
      console.warn('[this1] WS construction failed', e);
      if (!stop) setTimeout(connect, 1000);
      return;
    }
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data && data.type === 'hello') return;
        onMessage(data);
      } catch {}
    };
    ws.onclose = (ev) => {
      console.warn('[this1] WS closed', ev.code, ev.reason);
      onClose && onClose();
      if (!stop) setTimeout(connect, 1500);
    };
    ws.onerror = (ev) => {
      console.warn('[this1] WS error', ev);
    };
    ws.onopen = () => {
      console.log('[this1] WS open');
      try { ws.send('hi'); } catch {}
      onOpen && onOpen();
    };
  }
  connect();
  return () => { stop = true; ws && ws.close(); };
}
