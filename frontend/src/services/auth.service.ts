import api from '@/api/client';
import type { AuthResponse, Employee } from '@/types';

export const authService = {
  async login(username: string, password: string) {
    const { data } = await api.post<AuthResponse>('/auth/login', { username, password });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('employee', JSON.stringify(data.employee));
    return data;
  },

  async getCurrentEmployee() {
    const { data } = await api.get<Employee>('/auth/me');
    return data;
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('employee');
  },
};
