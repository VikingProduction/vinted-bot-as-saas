// frontend/src/components/SubscriptionPlans.tsx
import React from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import PaymentForm from '../components/PaymentForm';

// Clé publique Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || '');

interface Plan {
  id: string;
  name: string;
  price: number;
  features: string[];
}

const plans: Plan[] = [
  { id: 'starter', name: 'Starter', price: 19.99, features: ['10 filtres', '200 alertes/jour', 'Snipping'] },
  { id: 'pro', name: 'Pro', price: 49.99, features: ['50 filtres', '1000 alertes/jour', 'Analytics'] },
  { id: 'business', name: 'Business', price: 99.99, features: ['Filtres illimités', 'Alertes illimitées', 'API Access'] },
];

const SubscriptionPlans: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Choisissez votre plan d'abonnement</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div key={plan.id} className="border rounded-lg p-6 shadow hover:shadow-lg transition">
            <h2 className="text-2xl font-semibold mb-4">{plan.name}</h2>
            <p className="text-xl font-bold mb-4">{plan.price}€/mois</p>
            <ul className="mb-6 space-y-2">
              {plan.features.map((feat) => (
                <li key={feat} className="flex items-center">
                  <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  {feat}
                </li>
              ))}
            </ul>
            <Elements stripe={stripePromise} options={{ clientSecret: plan.id }}>
              <PaymentForm planId={plan.id} />
            </Elements>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubscriptionPlans;
