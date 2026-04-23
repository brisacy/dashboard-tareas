import { ref } from 'vue';
import { api } from '../Api.js';

const notifications = ref([]);
const unreadCount = ref(0);
let ws = null;

export function useNotifications() {
  
  const connectWebSocket = () => {
    if (ws) return; // Ya conectado

    const token = localStorage.getItem('access');
    if (!token) return;

    // Conectar a WS con el token
    ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`);

    ws.onopen = () => {
      console.log("WebSocket de Notificaciones Conectado.");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // data: { type: 'DIRECT'|'PUBLIC', action: '...', message: '...' }
      
      notifications.value.unshift(data);
      unreadCount.value++;
    };

    ws.onclose = () => {
      console.log("WebSocket Desconectado. Reintentando en 3s...");
      ws = null;
      setTimeout(connectWebSocket, 3000);
    };
  };

  const loadHistory = async () => {
    try {
      const { data } = await api.get('notifications/');
      notifications.value = Array.isArray(data) ? data : [];
      unreadCount.value = notifications.value.filter(n => !n.is_read).length;
    } catch (e) {
      console.error("Error cargando notificaciones", e);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.post('notifications/mark_all_read/');
      unreadCount.value = 0;
      notifications.value.forEach(n => n.is_read = true);
    } catch (e) {
      console.error("Error marcando como leídas", e);
    }
  };

  const initNotifications = () => {
    loadHistory();
    connectWebSocket();
  };

  return {
    notifications,
    unreadCount,
    markAllAsRead,
    initNotifications
  };
}
