// Configuración del juego
export const CONFIG = {
    // Configuración del WebSocket
    WEBSOCKET: {
        URL: 'ws://localhost:8000',
        RECONNECT_ATTEMPTS: 5,
        RECONNECT_DELAY_BASE: 1000, // ms
        RECONNECT_DELAY_MAX: 10000, // ms
        PING_INTERVAL: 30000, // ms
        CONNECTION_TIMEOUT: 10000, // ms
    },

    // Configuración del juego
    GAME: {
        INITIAL_REPUTATION: 20,
        MAX_HAND_SIZE: 7,
        INITIAL_HAND_SIZE: 5,
        MAX_DECK_SIZE: 30,
        TURN_TIME_LIMIT: 120000, // 2 minutos en ms
    },

    // Configuración de la UI
    UI: {
        ANIMATION_DURATION: 300,
        CARD_HOVER_DELAY: 500,
        TOAST_DURATION: 3000,
        DEBUG_MODE: true, // Set to false for production
    },

    // Logs y debugging
    DEBUG: {
        WEBSOCKET_LOGS: true,
        GAME_STATE_LOGS: false,
        PERFORMANCE_LOGS: false,
    }
};

export default CONFIG;