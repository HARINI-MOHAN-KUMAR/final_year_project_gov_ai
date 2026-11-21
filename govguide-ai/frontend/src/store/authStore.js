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

  clearError: () => set({ error: null }),

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const res = await api.post('/auth/login', {
        email,
        password,
      });

      const { access_token } = res.data;
      localStorage.setItem('govguide_token', access_token);

      // Fetch user profile
      const userRes = await api.get('/auth/me');

      localStorage.setItem('govguide_user', JSON.stringify(userRes.data));
      set({ token: access_token, user: userRes.data, isLoading: false, error: null });
      return { success: true };
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        (err.response?.status === 401
          ? 'Invalid email or password. Please try again.'
          : 'Login failed. Please check your credentials.');
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
      const msg = err.response?.data?.detail || 'Registration failed. Please try again.';
      set({ error: msg, isLoading: false });
      return { success: false, error: msg };
    }
  },

  logout: () => {
    localStorage.removeItem('govguide_token');
    localStorage.removeItem('govguide_user');
    set({ user: null, token: null, error: null });
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
      const msg = err.response?.data?.detail || err.message || 'Update failed.';
      set({ isLoading: false, error: msg });
      return { success: false, error: msg };
    }
  },
}));
