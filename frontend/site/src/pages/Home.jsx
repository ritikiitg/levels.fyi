import { useEffect, useState } from 'react';
import { api } from '../api.js';
import SalaryCard from '../components/SalaryCard.jsx';

export default function Home() {
  const [items, setItems] = useState([]);
  const [q, setQ] = useState('');
  const [err, setErr] = useState(null);

  useEffect(() => {
    api('/api/salaries?limit=30').then(setItems).catch((e) => setErr(String(e)));
  }, []);

  const filtered = items.filter((s) => {
    const hay = `${s.company} ${s.title} ${s.location} ${s.level}`.toLowerCase();
    return hay.includes(q.toLowerCase());
  });

  return (
    <div>
      <div className="mb-8">
        <h1 className="display text-5xl text-ink-950">Compensation Data</h1>
        <p className="text-ink-500 mt-2">Mock data only — for the bot-defense demo.</p>
      </div>
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search company, role, location…"
        className="w-full border border-ink-100 rounded-full px-5 py-3 mb-8 bg-white text-ink-950 focus:outline-none focus:border-gbg focus:ring-2 focus:ring-gbg/20 transition"
      />
      {err && <div className="text-gred text-sm mb-4">{err}</div>}
      <div className="grid gap-3">
        {filtered.map((s) => <SalaryCard key={s.uuid} s={s} />)}
        {filtered.length === 0 && !err && <div className="text-ink-500 text-sm text-center py-8">No results.</div>}
      </div>
    </div>
  );
}
