// frontend/src/services/auth.ts
import api from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Login utilisateur
export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/login', credentials);
  const { access_token } = response.data;
  localStorage.setItem('access_token', access_token);
  return response.data;
};

// Logout utilisateur
export const logout = () => {
  localStorage.removeItem('access_token');
};

// Récupérer l'utilisateur courant
export const getCurrentUser = async () => {
  const response = await api.get('/users/me');
  return response.data;
};
