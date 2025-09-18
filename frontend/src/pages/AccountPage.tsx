import { useEffect, useState } from "react";

type Limits = { filters: number; checks_per_min: number };

export default function AccountPage() {
  const [limits, setLimits] = useState<Limits | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(`${import.meta.env.VITE_API_URL || "/api"}/limits`, {
      headers: { "Authorization": `Bearer ${token}` }
    }).then(r => r.json()).then(setLimits);
  }, []);

  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl mb-2">Mon compte</h1>
      <div className="rounded-xl border p-4">
        <div className="text-sm opacity-70">Mes limites actuelles</div>
        {limits ? (
          <ul className="list-disc ml-6">
            <li>Filtres actifs: {limits.filters}</li>
            <li>Vérifications par minute: {limits.checks_per_min}</li>
          </ul>
        ) : <div>Chargement…</div>}
      </div>
    </div>
  );
}
