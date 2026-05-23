import { useEffect, useRef, useState } from 'react';

export default function StatCard({ label, value, sub, color = 'text-ink-950', accent }) {
  const prev = useRef(value);
  const [flash, setFlash] = useState(false);

  useEffect(() => {
    if (prev.current !== value) {
      setFlash(true);
      const t = setTimeout(() => setFlash(false), 500);
      prev.current = value;
      return () => clearTimeout(t);
    }
  }, [value]);

  return (
    <div className="panel panel-accent px-4 py-3 relative overflow-hidden" style={{ '--accent': accent || '#1A73E8' }}>
      <div className="flex items-baseline justify-between gap-2">
        <div className="eyebrow !text-[10px]">{label}</div>
        <div className={`stat-num text-2xl ${color} ${flash ? 'num-flash' : ''}`}>{value}</div>
      </div>
      {sub && <div className="text-[11px] text-ink-500 mt-1 leading-tight">{sub}</div>}
    </div>
  );
}
