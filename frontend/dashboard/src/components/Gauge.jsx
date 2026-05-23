export default function Gauge({ value = 0, label = 'Bot rate', sub }) {
  const pct = Math.max(0, Math.min(100, value));
  const r = 28;
  const C = 2 * Math.PI * r;
  const offset = C * (1 - pct / 100);
  const color = pct >= 50 ? '#EA4335' : pct >= 20 ? '#FBBC04' : '#34A853';

  return (
    <div className="panel panel-accent px-4 py-3 relative overflow-hidden" style={{ '--accent': color }}>
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="eyebrow !text-[10px]">{label}</div>
          <div className="stat-num text-2xl mt-0.5" style={{ color }}>
            {pct.toFixed(0)}<span className="text-base text-ink-500">%</span>
          </div>
        </div>
        <svg width="64" height="64" viewBox="0 0 64 64" className="-rotate-90 flex-shrink-0">
          <circle cx="32" cy="32" r={r} fill="none" strokeWidth="5" className="gauge-track" />
          <circle
            cx="32" cy="32" r={r} fill="none" strokeWidth="5"
            strokeLinecap="round"
            stroke={color}
            strokeDasharray={C}
            strokeDashoffset={offset}
            className="gauge-fill"
          />
        </svg>
      </div>
      {sub && <div className="text-[11px] text-ink-500 mt-1 leading-tight truncate">{sub}</div>}
    </div>
  );
}
