const COLOR = {
  human: 'text-ggrn',
  watch: 'text-gyel',
  suspicious: 'text-gyel',
  bot: 'text-gred',
};

const ACTION_BADGE = {
  allow:     'bg-green-50 text-green-700 border-green-200',
  challenge: 'bg-yellow-50 text-yellow-800 border-yellow-200',
  decoy:     'bg-red-50 text-red-700 border-red-200',
};

function fmtTime(ts) {
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString('en-US', { hour12: false });
}

export default function LiveFeed({ events }) {
  return (
    <div className="panel overflow-hidden">
      <div className="px-5 py-4 border-b border-ink-100 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="w-1.5 h-1.5 bg-ggrn rounded-full scroll-pulse" />
          <h2 className="display text-lg text-ink-950">Live feed</h2>
        </div>
        <span className="eyebrow !text-[10px]">{events.length} events</span>
      </div>
      <div className="max-h-[60vh] overflow-y-auto font-mono text-xs">
        {events.map((e, i) => {
          const rowClass = e.verdict === 'bot' ? 'pulse-bg-bot'
                         : (e.verdict === 'suspicious' ? 'pulse-bg-warn' : '');
          return (
            <div
              key={i}
              className={`px-5 py-2.5 border-b border-ink-100/70 flex items-center gap-3 ${rowClass} hover:bg-paper-soft transition-colors`}
            >
              <span className="text-ink-500 w-20 flex-shrink-0">{fmtTime(e.ts)}</span>
              <span className="text-ink-700 w-28 truncate flex-shrink-0">{e.ip}</span>
              <span className="text-ink-500 w-10 flex-shrink-0">{e.method}</span>
              <span className="text-ink-950 flex-1 truncate">{e.path}</span>
              <span className={`w-28 text-right flex-shrink-0 font-semibold ${COLOR[e.verdict] || 'text-ink-500'}`}>
                {e.verdict} · {Number(e.suspicion).toFixed(2)}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wider border ${ACTION_BADGE[e.action] || 'bg-paper-mid text-ink-500'}`}>
                {e.action}
              </span>
            </div>
          );
        })}
        {events.length === 0 && (
          <div className="px-4 py-16 text-center text-ink-500">
            <div className="text-4xl mb-3">⚡</div>
            <div className="display text-lg mb-1 text-ink-950">Awaiting traffic</div>
            <div className="text-xs">Click any scenario on the right to launch one.</div>
          </div>
        )}
      </div>
    </div>
  );
}
