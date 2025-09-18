// Types globaux pour l'application Vinted Bot SaaS

export interface User {
  id: string;
  email: string;
  name: string;
  subscription?: Subscription;
}

export interface VintedFilter {
  id: string;
  name: string;
  criteria: FilterCriteria;
  isActive: boolean;
  userId: string;
}

export interface FilterCriteria {
  brand?: string;
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  size?: string;
  condition?: string;
}

export interface Subscription {
  id: string;
  plan: 'starter' | 'pro' | 'business';
  status: 'active' | 'inactive' | 'cancelled';
  currentPeriodEnd: string;
}

export interface Alert {
  id: string;
  filterId: string;
  itemUrl: string;
  itemTitle: string;
  itemPrice: number;
  createdAt: string;
}
