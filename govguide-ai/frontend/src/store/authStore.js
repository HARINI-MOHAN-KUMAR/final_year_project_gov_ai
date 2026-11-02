import { create } from 'zustand';
import api from '../api/client';

const safeGetJSON = (key, fallback = null) => {
  try {
    const val = localStorage.getItem(key);
    if (!val || val === 'undefined' || val === 'null') return fallback;
    return JSON.parse(val);
  } catch (err) {
    return fallback;
  }
};

const safeGetItem = (key, fallback = null) => {
  try {
    return localStorage.getItem(key) || fallback;
  } catch (err) {
    return fallback;
  }
};

export const useAuthStore = create((set, get) => ({
  user: safeGetJSON('govguide_user', null),
  token: safeGetItem('govguide_token', null),
  language: safeGetItem('govguide_lang', 'en'),
  isLoading: false,
  error: null,

  setLanguage: (lang) => {
    localStorage.setItem('govguide_lang', lang);
    set({ language: lang });
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const { access_token } = res.data;
      localStorage.setItem('govguide_token', access_token);

      // Fetch user profile
      const userRes = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      });

      localStorage.setItem('govguide_user', JSON.stringify(userRes.data));
      set({ token: access_token, user: userRes.data, isLoading: false });
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      set({ error: msg, isLoading: false });
      return { success: false, error: msg };
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      await api.post('/auth/register', userData);
      // Auto login after registration
      return await get().login(userData.email, userData.password);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed.';
      set({ error: msg, isLoading: false });
      return { success: false, error: msg };
    }
  },

  logout: () => {
    localStorage.removeItem('govguide_token');
    localStorage.removeItem('govguide_user');
    set({ user: null, token: null });
  },

  fetchProfile: async () => {
    try {
      const res = await api.get('/profile/');
      set({ user: res.data });
      localStorage.setItem('govguide_user', JSON.stringify(res.data));
      return res.data;
    } catch (err) {
      console.error('Failed to fetch profile', err);
    }
  },

  updateProfile: async (data) => {
    set({ isLoading: true });
    try {
      const res = await api.put('/profile/', data);
      set({ user: res.data, isLoading: false });
      localStorage.setItem('govguide_user', JSON.stringify(res.data));
      return { success: true, data: res.data };
    } catch (err) {
      set({ isLoading: false, error: err.message });
      return { success: false, error: err.message };
    }
  },
}));
