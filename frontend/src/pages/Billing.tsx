import { useState } from "react";
import { getStripe } from "../lib/stripe";

const PRICES = {
  basic: import.meta.env.VITE_STRIPE_PRICE_BASIC || "price_basic_placeholder",
  pro:   import.meta.env.VITE_STRIPE_PRICE_PRO   || "price_pro_placeholder",
  elite: import.meta.env.VITE_STRIPE_PRICE_ELITE || "price_elite_placeholder",
};

export default function Billing() {
  const [loading, setLoading] = useState<string | null>(null);

  const startCheckout = async (priceId: string) => {
    setLoading(priceId);
    const token = localStorage.getItem("token");
    const res = await fetch(`${import.meta.env.VITE_API_URL || "/api"}/billing/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ price_id: priceId })
    });
    const data = await res.json();
    setLoading(null);
    window.location.href = data.url;  // redirection Stripe Checkout
  };

  const openPortal = async () => {
    const token = localStorage.getItem("token");
    const res = await fetch(`${import.meta.env.VITE_API_URL || "/api"}/billing/portal`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await res.json();
    window.location.href = data.url;
  };

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <h1 className="text-2xl">Abonnement</h1>
      <div className="grid gap-3">
        {Object.entries(PRICES).map(([code, pid]) => (
          <button key={code}
            onClick={() => startCheckout(pid as string)}
            disabled={loading === pid}
            className="px-4 py-2 rounded-xl border">
            Souscrire {code.toUpperCase()}
          </button>
        ))}
      </div>
      <hr />
      <button onClick={openPortal} className="px-4 py-2 rounded-xl border">Gérer mon abonnement</button>
    </div>
  );
}
