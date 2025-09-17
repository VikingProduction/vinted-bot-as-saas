// frontend/src/components/PaymentForm.tsx
import React from 'react';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import api from '../services/api';

interface PaymentFormProps {
  planId: string;
}

const PaymentForm: React.FC<PaymentFormProps> = ({ planId }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setLoading(true);
    setError(null);
    
    // Créer la session de paiement côté backend
    const session = await api.post('/subscriptions/create_session', { plan: planId });
    const { clientSecret } = session.data;

    // Confirmation du paiement
    const cardElement = elements.getElement(CardElement);
    if (!cardElement) return;

    const { error } = await stripe.confirmCardPayment(clientSecret, {
      payment_method: { card: cardElement }
    });

    if (error) {
      setError(error.message || 'Erreur de paiement');
      setLoading(false);
    } else {
      // Redirection vers utilisateurs ou mise à jour de l'état
      window.location.reload();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <CardElement options={{ hidePostalCode: true }} />
      {error && <p className="text-red-500">{error}</p>}
      <button
        type="submit"
        disabled={!stripe || loading}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Chargement...' : 'Souscrire'}
      </button>
    </form>
  );
};

export default PaymentForm;
