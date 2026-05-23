import { useEffect, useState } from 'react';
import { api, apiPost } from '../api.js';

const META = {
  'naive-scraper':       { dot: '#EA4335', tag: 'L3' },
  'polite-scraper':      { dot: '#FBBC04', tag: 'L2' },
  'distributed':         { dot: '#FBBC04', tag: 'L2' },
  'credential-stuffer':  { dot: '#EA4335', tag: 'L3' },
  'slow-and-low':        { dot: '#9C27B0', tag: 'L1' },
};

export default function AttackPanel() {
  const [scenarios, setScenarios] = useState([]);
  const [running, setRunning] = useState({});
  const [err, setErr] = useState(null);

  useEffect(() => {
    api('/api/dashboard/scenarios').then((d) => setScenarios(d.scenarios || [])).catch((e) => setErr(String(e)));
    const t = setInterval(() => {
      api('/api/dashboard/simulate/status').then(setRunning).catch(() => {});
    }, 1500);
    return () => clearInterval(t);
  }, []);

  async function launch(id) {
    setErr(null);
    try { await apiPost(`/api/dashboard/simulate?scenario=${id}&duration=15&qps=5`); }
    catch (e) { setErr(String(e)); }
  }

  async function stopAll() {
    try { await apiPost(`/api/dashboard/simulate/stop`); }
    catch (e) { setErr(String(e)); }
  }

  const anyRunning = Object.values(running).some((r) => r && !r.done);

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="display text-lg text-ink-950">Launch attack</h3>
        <button onClick={stopAll} className="btn-ghost !text-[10px] !uppercase !tracking-widest !py-1 !px-3">
          stop all
        </button>
      </div>
      <p className="text-xs text-ink-500 mb-4">15-second scripted attack against the local backend.</p>
      {anyRunning && (
        <div className="relative mb-3 h-1 rounded-full overflow-hidden bg-paper-mid">
          <div className="absolute inset-0 scanner" />
        </div>
      )}
      <div className="grid grid-cols-1 gap-2">
        {scenarios.map((s) => {
          const r = running[s.id];
          const isRunning = r && !r.done;
          const meta = META[s.id] || { dot: '#5F6368', tag: '·' };
          return (
            <button
              key={s.id}
              onClick={() => launch(s.id)}
              disabled={isRunning}
              className={`group text-left rounded-xl p-3 border transition-all duration-200
                          ${isRunning
                            ? 'border-gbg/40 bg-blue-50'
                            : 'border-ink-100 bg-white hover:border-ink-300 hover:-translate-y-0.5 hover:shadow-md'}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ background: meta.dot, boxShadow: `0 0 8px ${meta.dot}` }}
                  />
                  <span className="font-mono text-[12px] text-ink-950 font-medium">{s.id}</span>
                </div>
                <span className="text-[9px] uppercase tracking-widest text-ink-500">
                  {isRunning ? 'running' : meta.tag}
                </span>
              </div>
              <div className="text-[11px] text-ink-500 mt-1.5 leading-snug">{s.description}</div>
            </button>
          );
        })}
      </div>
      {err && <div className="text-xs text-gred mt-2">{err}</div>}
    </div>
  );
}
