import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const COLOR = {
  human: '#34A853',
  watch: '#FBBC04',
  suspicious: '#FBBC04',
  bot: '#EA4335',
};

export default function VerdictChart({ events }) {
  const buckets = {};
  events.forEach((e) => { buckets[e.verdict] = (buckets[e.verdict] || 0) + 1; });
  const data = Object.entries(buckets).map(([k, v]) => ({ name: k, count: v, fill: COLOR[k] || '#9AA0A6' }));

  return (
    <div className="panel p-5 h-full">
      <h3 className="display text-lg mb-3 text-ink-950">Verdicts</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <XAxis dataKey="name" stroke="#5F6368" fontSize={11} />
          <YAxis stroke="#5F6368" fontSize={11} />
          <Tooltip contentStyle={{ background: '#fff', border: '1px solid #E8EAED', borderRadius: 8 }} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
