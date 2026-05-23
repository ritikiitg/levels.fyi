import { useEffect, useMemo, useRef, useState } from 'react';
import { api, openLiveFeed } from './api.js';
import StatCard from './components/StatCard.jsx';
import LiveFeed from './components/LiveFeed.jsx';
import VerdictChart from './components/VerdictChart.jsx';
import TopIPs from './components/TopIPs.jsx';
import ConfusionMatrix from './components/ConfusionMatrix.jsx';
import Gauge from './components/Gauge.jsx';
import AttackPanel from './components/AttackPanel.jsx';
import KillChain from './components/KillChain.jsx';

const MAX_EVENTS = 250;

export default function App() {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const [serverTotal, setServerTotal] = useState(0);
  const seedDone = useRef(false);

  useEffect(() => {
    if (seedDone.current) return;
    seedDone.current = true;
    api('/api/dashboard/feed?limit=100')
      .then((rows) => {
        setEvents(rows.map((r) => ({
          ts: r.ts, ip: r.ip, method: r.method, path: r.path,
          ua: r.user_agent, status: r.status,
          suspicion: r.suspicion ?? 0, verdict: r.verdict ?? 'human',
          action: r.action ?? 'allow',
        })).reverse());
      })
      .catch(() => {});

    const close = openLiveFeed(
      (ev) => setEvents((cur) => [...cur, ev].slice(-MAX_EVENTS)),
      () => setConnected(true),
      () => setConnected(false),
    );

    // Poll the backend for the authoritative request count — the local
    // events array is capped at 250, but the server has the full picture.
    const pollSummary = () => {
      api('/api/dashboard/summary?window_seconds=3600')
        .then((s) => setServerTotal(s.total || 0))
        .catch(() => {});
    };
    pollSummary();
    const t = setInterval(pollSummary, 2000);

    return () => { close(); clearInterval(t); };
  }, []);

  const stats = useMemo(() => {
    const counts = { human: 0, watch: 0, suspicious: 0, bot: 0 };
    events.forEach((e) => { counts[e.verdict] = (counts[e.verdict] || 0) + 1; });
    const total = events.length || 1;
    const decoyed = events.filter((e) => e.action === 'decoy').length;
    return { ...counts, total: events.length, decoyed, botRate: ((counts.bot / total) * 100).toFixed(1) };
  }, [events]);

  const lastEvent = events.length ? events[events.length - 1] : null;

  return (
    <div className="min-h-screen">
      <header className="border-b border-ink-100 px-6 py-4 flex items-center justify-between sticky top-0 z-10 bg-white/85 backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <img src="/logo.png" alt="this1" className="w-11 h-11 rounded-xl logo-glow float-soft" />
          <div>
            <h1 className="wordmark text-3xl leading-none">
              <span className="this">this</span><span className="one">1</span>
            </h1>
            <div className="text-[11px] text-ink-500 mt-1.5">Adaptive bot defense · Levels.fyi</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right text-xs">
            <div className="text-ink-950 font-mono">{serverTotal.toLocaleString()}</div>
            <div className="eyebrow !text-[9px]">requests · last hour</div>
          </div>
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${connected ? 'border-ggrn/40 bg-green-50' : 'border-ink-100 bg-white'}`}>
            <span className={`w-2 h-2 rounded-full ${connected ? 'bg-ggrn live-dot' : 'bg-ink-300'}`} />
            <span className={`text-xs ${connected ? 'text-ggrn font-medium' : 'text-ink-500'}`}>
              {connected ? 'live' : 'connecting…'}
            </span>
          </div>
        </div>
      </header>

      <main className="p-6 grid gap-5 max-w-[1600px] mx-auto">
        <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <Gauge value={parseFloat(stats.botRate)} label="Bot rate" sub="of recent traffic" />
          <StatCard label="Human"      value={stats.human}                       color="text-ggrn"  accent="#34A853" sub="sailing through" />
          <StatCard label="Watch+Susp" value={stats.suspicious + stats.watch}    color="text-gyel"  accent="#FBBC04" sub="CAPTCHA challenged" />
          <StatCard label="Confirmed"  value={stats.bot}                         color="text-gred"  accent="#EA4335" sub="suspicion ≥ 0.75" />
          <StatCard label="Decoyed"    value={stats.decoyed}                     color="text-gred"  accent="#9C27B0" sub="served fake data" />
        </section>

        <KillChain lastEvent={lastEvent} />

        <section className="grid grid-cols-12 gap-5">
          <div className="col-span-12 lg:col-span-8"><LiveFeed events={[...events].reverse()} /></div>
          <div className="col-span-12 lg:col-span-4 grid gap-5">
            <AttackPanel />
            <TopIPs events={events} />
          </div>
        </section>

        <section className="grid grid-cols-12 gap-5">
          <div className="col-span-12 lg:col-span-4"><VerdictChart events={events} /></div>
          <div className="col-span-12 lg:col-span-4"><ConfusionMatrix /></div>
          <div className="col-span-12 lg:col-span-4 panel p-5">
            <div className="eyebrow mb-3">How it works</div>
            <h3 className="display text-xl mb-3 text-ink-950">Three layers between scrapers and your data</h3>
            <ol className="space-y-2.5 text-xs text-ink-700">
              <li className="flex gap-3 items-start">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-green-50 text-ggrn border border-green-200 mt-0.5">L0</span>
                <span>Verified search engines whitelisted by reverse-DNS</span>
              </li>
              <li className="flex gap-3 items-start">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-50 text-gbg border border-blue-200 mt-0.5">L1</span>
                <span>Invisible proof-of-work on every page (50ms, humans never notice)</span>
              </li>
              <li className="flex gap-3 items-start">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-yellow-50 text-yellow-700 border border-yellow-200 mt-0.5">L2</span>
                <span>In-house CAPTCHA when suspicion ≥ 0.5</span>
              </li>
              <li className="flex gap-3 items-start">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-red-50 text-gred border border-red-200 mt-0.5">L3</span>
                <span>Confirmed bots get <span className="text-gred font-semibold">decoy data</span> — silently poisoned</span>
              </li>
            </ol>
            <div className="mt-4 pt-3 border-t border-ink-100 text-[11px] text-ink-500">
              Click a scenario at right ↗ to fire an attack and watch every layer light up.
            </div>
          </div>
        </section>

        <footer className="text-center text-[10px] text-ink-500 tracking-widest uppercase py-4">
          this1 · built for the Levels.fyi hackathon
        </footer>
      </main>
    </div>
  );
}
