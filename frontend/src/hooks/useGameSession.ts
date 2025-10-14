import { useState, useEffect, useCallback } from 'react';

interface GameSession {
    gameId: string;
    playerId: string;
    view: 'setup' | 'game';
    timestamp: number;
}

export const useGameSession = () => {
    const [session, setSession] = useState<GameSession | null>(null);

    const loadSession = useCallback(() => {
        try {
            const saved = localStorage.getItem('chaosCity_gameSession');
            if (saved) {
                const parsed = JSON.parse(saved) as GameSession;
                // Solo cargar sesiones de menos de 24 horas
                if (Date.now() - parsed.timestamp < 24 * 60 * 60 * 1000) {
                    setSession(parsed);
                    return parsed;
                }
            }
        } catch (error) {
            console.warn('Failed to load game session:', error);
        }
        return null;
    }, []);

    const saveSession = useCallback((gameId: string, playerId: string, view: 'setup' | 'game') => {
        try {
            const newSession: GameSession = {
                gameId,
                playerId,
                view,
                timestamp: Date.now()
            };
            localStorage.setItem('chaosCity_gameSession', JSON.stringify(newSession));
            setSession(newSession);
        } catch (error) {
            console.warn('Failed to save game session:', error);
        }
    }, []);

    const clearSession = useCallback(() => {
        try {
            localStorage.removeItem('chaosCity_gameSession');
            setSession(null);
        } catch (error) {
            console.warn('Failed to clear game session:', error);
        }
    }, []);

    // Cargar sesión al inicializar el hook
    useEffect(() => {
        loadSession();
    }, []);

    return {
        session,
        saveSession,
        clearSession,
        loadSession
    };
};

export default useGameSession;