export default function TopIPs({ events }) {
  const tally = new Map();
  events.forEach((e) => {
    const t = tally.get(e.ip) || { ip: e.ip, count: 0, maxSusp: 0, lastVerdict: e.verdict };
    t.count += 1;
    t.maxSusp = Math.max(t.maxSusp, e.suspicion || 0);
    t.lastVerdict = e.verdict;
    tally.set(e.ip, t);
  });
  const rows = [...tally.values()].sort((a, b) => b.maxSusp - a.maxSusp).slice(0, 8);

  return (
    <div className="panel p-5 flex flex-col" style={{ maxHeight: 360 }}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="display text-lg text-ink-950">Top IPs by suspicion</h3>
        <span className="eyebrow !text-[10px]">{rows.length}</span>
      </div>
      {rows.length === 0 ? (
        <div className="text-xs text-ink-500 py-6 text-center">No traffic yet.</div>
      ) : (
        <div className="overflow-y-auto flex-1 -mx-1 px-1">
          <table className="w-full text-sm">
            <thead className="text-[10px] uppercase tracking-widest text-ink-500 sticky top-0 bg-white">
              <tr>
                <th className="text-left py-1">IP</th>
                <th className="text-right py-1">Reqs</th>
                <th className="text-right py-1">Max susp.</th>
                <th className="text-right py-1">Last</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.ip} className="border-t border-ink-100 hover:bg-paper-soft transition-colors">
                  <td className="py-1.5 font-mono text-xs text-ink-950">{r.ip}</td>
                  <td className="py-1.5 text-right text-ink-700">{r.count}</td>
                  <td className={`py-1.5 text-right font-medium ${r.maxSusp >= 0.9 ? 'text-gred' : r.maxSusp >= 0.5 ? 'text-gyel' : 'text-ink-700'}`}>
                    {r.maxSusp.toFixed(2)}
                  </td>
                  <td className="py-1.5 text-right text-xs text-ink-500">{r.lastVerdict}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
