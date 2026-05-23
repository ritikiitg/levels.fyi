import { useEffect, useState } from 'react';
import { api } from '../api.js';

export default function ConfusionMatrix() {
  const [info, setInfo] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    api('/api/model/info').then(setInfo).catch((e) => setErr(String(e)));
  }, []);

  if (err) return (
    <div className="panel p-5">
      <h3 className="display text-lg mb-2 text-ink-950">Model metrics</h3>
      <div className="text-xs text-gyel">
        Train the model first: <code className="bg-paper-mid px-1.5 py-0.5 rounded font-mono text-ink-700">python -m ml.train</code>
      </div>
    </div>
  );
  if (!info) return null;

  const [[tn, fp], [fn, tp]] = info.confusion;
  const total = tn + fp + fn + tp;
  const accuracy = ((tn + tp) / total * 100).toFixed(2);
  const fpr = (fp / (fp + tn) * 100).toFixed(2);
  const recall = (tp / (tp + fn) * 100).toFixed(2);

  const importances = Object.entries(info.feature_importances)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);

  return (
    <div className="panel p-5">
      <h3 className="display text-lg mb-4 text-ink-950">Model metrics</h3>
      <div className="grid grid-cols-2 gap-2 text-xs mb-4">
        <div className="bg-paper-soft border border-ink-100 rounded-lg p-2 text-center">
          <div className="eyebrow !text-[9px]">TN</div>
          <div className="stat-num text-2xl text-ggrn mt-1">{tn}</div>
        </div>
        <div className="bg-paper-soft border border-ink-100 rounded-lg p-2 text-center">
          <div className="eyebrow !text-[9px]">FP</div>
          <div className="stat-num text-2xl text-gyel mt-1">{fp}</div>
        </div>
        <div className="bg-paper-soft border border-ink-100 rounded-lg p-2 text-center">
          <div className="eyebrow !text-[9px]">FN</div>
          <div className="stat-num text-2xl text-gred mt-1">{fn}</div>
        </div>
        <div className="bg-paper-soft border border-ink-100 rounded-lg p-2 text-center">
          <div className="eyebrow !text-[9px]">TP</div>
          <div className="stat-num text-2xl text-ggrn mt-1">{tp}</div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-xs mb-4">
        <div>
          <div className="eyebrow !text-[9px]">Accuracy</div>
          <div className="stat-num text-xl text-ink-950 mt-1">{accuracy}%</div>
        </div>
        <div>
          <div className="eyebrow !text-[9px]">Recall (bot)</div>
          <div className="stat-num text-xl text-ink-950 mt-1">{recall}%</div>
        </div>
        <div>
          <div className="eyebrow !text-[9px]">FP rate</div>
          <div className="stat-num text-xl text-ink-950 mt-1">{fpr}%</div>
        </div>
      </div>
      <div className="eyebrow !text-[10px] mb-2">Top features</div>
      <div className="space-y-1.5">
        {importances.map(([name, v]) => (
          <div key={name} className="flex items-center gap-2 text-xs">
            <div className="w-32 truncate text-ink-700">{name}</div>
            <div className="flex-1 bg-paper-mid rounded-full h-1.5 overflow-hidden">
              <div className="bg-gbg h-1.5 rounded-full transition-all duration-500" style={{ width: `${Math.min(100, v * 100 * 4)}%` }} />
            </div>
            <div className="w-12 text-right text-ink-500 tabular-nums">{(v * 100).toFixed(1)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}
