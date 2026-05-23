import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api.js';

function fmt(n, ccy) {
  if (n == null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: ccy || 'USD', maximumFractionDigits: 0 }).format(n);
}

export default function Salary() {
  const { uuid } = useParams();
  const [s, setS] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    api(`/api/salaries/${uuid}`).then(setS).catch((e) => setErr(String(e)));
  }, [uuid]);

  if (err) return <div className="text-gred">{err}</div>;
  if (!s) return <div className="text-ink-500">Loading…</div>;

  return (
    <div className="card p-8">
      <div className="text-xs uppercase tracking-widest text-ink-500">{s.company}</div>
      <h1 className="display text-3xl text-ink-950 mt-1">{s.title} · {s.level}</h1>
      <div className="text-ink-500 mb-8 mt-1">{s.location} · {s.workArrangement}</div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Stat label="Base" value={fmt(s.baseSalary, s.baseSalaryCurrency)} />
        <Stat label="Stock (annual)" value={fmt(s.avgAnnualStockGrantValue, s.stockGrantCurrency)} />
        <Stat label="Bonus" value={fmt(s.avgAnnualBonusValue, s.bonusCurrency)} />
        <Stat label="Total" value={fmt(s.totalCompensation, s.baseSalaryCurrency)} highlight />
      </div>

      <div className="mt-8 text-sm text-ink-700 space-y-1.5">
        <div><span className="text-ink-500">Years of experience:</span> {s.yearsOfExperience}</div>
        <div><span className="text-ink-500">Years at company:</span> {s.yearsAtCompany}</div>
        <div><span className="text-ink-500">Offer date:</span> {s.offerDate}</div>
      </div>
    </div>
  );
}

function Stat({ label, value, highlight }) {
  return (
    <div className={`rounded-xl border p-4 ${highlight ? 'border-gbg bg-blue-50' : 'border-ink-100 bg-paper-soft'}`}>
      <div className="text-[10px] uppercase tracking-widest text-ink-500">{label}</div>
      <div className={`display text-lg mt-1 ${highlight ? 'text-gbg' : 'text-ink-950'}`}>{value}</div>
    </div>
  );
}
