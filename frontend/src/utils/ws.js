const API_HOST = import.meta.env.VITE_API_WS_URL || 'localhost:8000';

export class WebSocketManager {
  constructor() {
    this.socket = null;
    this.handlers = {};
    this.roomId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect(roomId, token, handlers) {
    if (this.socket) {
      this.disconnect();
    }

    this.roomId = roomId;
    this.handlers = handlers;
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const isDm = roomId.startsWith('dm_');
    const endpoint = isDm ? `dm/${roomId.replace('dm_', '')}` : roomId;
    const url = `${protocol}://${API_HOST}/ws/${endpoint}?token=${token}`;

    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log(`Connected to room: ${roomId}`);
      this.reconnectAttempts = 0;
      if (this.handlers.onConnect) this.handlers.onConnect();
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (this.handlers.onMessage) {
        this.handlers.onMessage(data);
      }
      // Dispatch a global event for system-wide updates (e.g., role changes)
      window.dispatchEvent(new CustomEvent('nexus_socket_message', { detail: data }));
    };

    this.socket.onclose = (event) => {
      console.log(`Disconnected from room: ${roomId}`);
      if (this.handlers.onDisconnect) this.handlers.onDisconnect();
      
      // Auto-reconnect if not intentionally closed
      // 1000 = normal closure, 4003 = kicked by admin
      if (event.code !== 1000 && event.code !== 4003 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const timeout = Math.pow(2, this.reconnectAttempts) * 1000;
        console.log(`Attempting reconnect in ${timeout}ms...`);
        setTimeout(() => this.connect(roomId, token, handlers), timeout);
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket Error:', error);
      if (this.handlers.onError) this.handlers.onError(error);
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close(1000); // Normal closure
      this.socket = null;
    }
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }
}

export const wsManager = new WebSocketManager();
export const dmWsManager = new WebSocketManager();
export default wsManager;
