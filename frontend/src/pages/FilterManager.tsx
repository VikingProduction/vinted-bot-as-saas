import { useState } from "react";

export default function FilterManager() {
  const [filters, setFilters] = useState<{query:string; active:boolean}[]>([]);
  const [q, setQ] = useState("");

  const add = () => {
    if (!q.trim()) return;
    setFilters(prev => [...prev, {query: q.trim(), active: true}]);
    setQ("");
  };

  return (
    <div className="border rounded-xl p-4 space-y-3">
      <div className="flex gap-2">
        <input className="flex-1 border rounded-lg px-3 py-2" value={q} onChange={e => setQ(e.target.value)} placeholder="mot-clé, catégorie, prix max…" />
        <button onClick={add} className="px-3 py-2 border rounded-lg">Ajouter</button>
      </div>
      <ul className="space-y-2">
        {filters.map((f,i)=>(
          <li key={i} className="flex items-center justify-between border rounded-lg px-3 py-2">
            <span>{f.query}</span>
            <button className="text-sm opacity-70">Désactiver</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
