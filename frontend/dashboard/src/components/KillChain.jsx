import { useEffect, useState } from 'react';

const LAYERS = [
  { id: 'allow',     label: 'Allow',    color: '#34A853', bg: 'rgba(52,168,83,0.10)',  desc: 'Trusted request' },
  { id: 'challenge', label: 'CAPTCHA',  color: '#FBBC04', bg: 'rgba(251,188,4,0.10)',  desc: 'Suspicion ≥ 0.5' },
  { id: 'decoy',     label: 'Decoy',    color: '#EA4335', bg: 'rgba(234,67,53,0.10)',  desc: 'Confirmed bot' },
];

export default function KillChain({ lastEvent }) {
  const [hits, setHits] = useState({ allow: 0, challenge: 0, decoy: 0 });
  const [flash, setFlash] = useState(null);

  useEffect(() => {
    if (!lastEvent) return;
    const action = lastEvent.action;
    if (!hits.hasOwnProperty(action)) return;
    setHits((h) => ({ ...h, [action]: (h[action] || 0) + 1 }));
    setFlash(action);
    const t = setTimeout(() => setFlash(null), 1300);
    return () => clearTimeout(t);
  }, [lastEvent]);

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="display text-lg text-ink-950">Defense pipeline</h3>
        <span className="eyebrow !text-[10px]">live</span>
      </div>
      <div className="flex items-center gap-4">
        {LAYERS.map((l, i) => (
          <div key={l.id} className="flex items-center flex-1">
            <div
              className={`flex-1 rounded-xl border-2 px-4 py-4 text-center transition-all duration-300 ${flash === l.id ? 'layer-fire' : ''}`}
              style={{
                borderColor: flash === l.id ? l.color : '#E8EAED',
                background: flash === l.id ? l.bg : '#ffffff',
              }}
            >
              <div className="stat-num text-3xl" style={{ color: l.color }}>{hits[l.id]}</div>
              <div className="text-xs font-mono mt-1" style={{ color: l.color }}>{l.label}</div>
              <div className="text-[10px] text-ink-500 mt-1">{l.desc}</div>
            </div>
            {i < LAYERS.length - 1 && (
              <div className="px-3 text-ink-300 text-xl">→</div>
            )}
          </div>
        ))}
      </div>
      <div className="mt-4 text-[11px] text-ink-500 text-center">
        Every request flows through the layers. Right = higher suspicion.
      </div>
    </div>
  );
}
