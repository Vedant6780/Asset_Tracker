/**
 * Centralized API helpers — fetch wrapper and WebSocket factory.
 */

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Make an authenticated fetch request.
 */
export async function authFetch(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        window.location.href = '/';
        throw new Error('Session expired');
    }

    return response;
}

/**
 * Create a WebSocket connection for the live dashboard.
 */
export function createDashboardSocket(onMessage, onOpen, onClose) {
    const token = localStorage.getItem('token');
    const ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/ws/dashboard?token=${token}`);

    ws.onopen = () => {
        console.log('🟢 WebSocket connected');
        onOpen?.();

        // Heartbeat every 30s
        const heartbeat = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send('ping');
            } else {
                clearInterval(heartbeat);
            }
        }, 30000);
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onMessage?.(data);
        } catch (e) {
            // Heartbeat pong — ignore
        }
    };

    ws.onclose = () => {
        console.log('🔴 WebSocket disconnected');
        onClose?.();
    };

    ws.onerror = (err) => {
        console.error('WebSocket error:', err);
    };

    return ws;
}
