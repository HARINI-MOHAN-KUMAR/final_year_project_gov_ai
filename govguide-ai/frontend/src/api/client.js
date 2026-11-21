import axios from 'axios';

const configuredApiOrigin = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '');

const api = axios.create({
  baseURL: configuredApiOrigin ? `${configuredApiOrigin}/api/v1` : '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const normalizeApiErrorDetail = (detail) => {
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (typeof item === 'string' ? item : item?.msg || item?.message))
      .filter(Boolean);
    return messages.length ? messages.join('; ') : 'Request validation failed.';
  }

  if (detail && typeof detail === 'object') {
    return detail.msg || detail.message || 'Request failed.';
  }

  return detail;
};

api.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem('govguide_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (e) {}
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const responseData = error.response?.data;
    if (responseData && typeof responseData === 'object' && 'detail' in responseData) {
      responseData.detail = normalizeApiErrorDetail(responseData.detail);
    }

    if (error.response && error.response.status === 401) {
      try {
        localStorage.removeItem('govguide_token');
        localStorage.removeItem('govguide_user');
      } catch (e) {}
    }
    return Promise.reject(error);
  }
);

export default api;
