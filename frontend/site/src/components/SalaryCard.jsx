import { Link } from 'react-router-dom';

function fmt(n, ccy) {
  if (n == null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: ccy || 'USD', maximumFractionDigits: 0 }).format(n);
}

export default function SalaryCard({ s }) {
  return (
    <Link to={`/salary/${s.uuid}`} className="card block p-5">
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <div className="text-xs text-ink-500 uppercase tracking-wider">{s.company}</div>
          <div className="display text-lg text-ink-950 mt-1 truncate">{s.title} · {s.level}</div>
          <div className="text-xs text-ink-500 mt-1">{s.location} · {s.yearsOfExperience}y exp</div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="display text-xl text-gbg">{fmt(s.totalCompensation, s.baseSalaryCurrency)}</div>
          <div className="text-[10px] uppercase tracking-widest text-ink-500 mt-1">total comp</div>
        </div>
      </div>
    </Link>
  );
}
