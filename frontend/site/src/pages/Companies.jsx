import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';

export default function Companies() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    api('/api/companies').then(setItems).catch(console.error);
  }, []);

  return (
    <div>
      <h1 className="display text-5xl text-ink-950 mb-8">Companies</h1>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {items.map((c) => (
          <Link key={c.company_slug} to={`/company/${c.company_slug}`} className="card block p-5">
            <div className="display text-lg text-ink-950">{c.company}</div>
            <div className="text-xs text-ink-500 mt-1">{c.submissions} submissions</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
