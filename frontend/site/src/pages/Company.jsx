import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api.js';
import SalaryCard from '../components/SalaryCard.jsx';

export default function Company() {
  const { slug } = useParams();
  const [items, setItems] = useState([]);

  useEffect(() => {
    api(`/api/salaries?company=${slug}&limit=100`).then(setItems).catch(console.error);
  }, [slug]);

  return (
    <div>
      <h1 className="display text-5xl text-ink-950 mb-8 capitalize">{slug}</h1>
      <div className="grid gap-3">
        {items.map((s) => <SalaryCard key={s.uuid} s={s} />)}
        {items.length === 0 && <div className="text-ink-500 text-sm">No salaries yet for this company.</div>}
      </div>
    </div>
  );
}
