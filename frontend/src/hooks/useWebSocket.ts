import { useState, useEffect, useCallback, useRef } from 'react';
import { GameState, WebSocketMessage, Faction, Zone } from '../types/game';
import { CONFIG } from '../config';

export const useWebSocket = (url: string) => {
    const [isConnected, setIsConnected] = useState(false);
    const [gameState, setGameState] = useState<GameState | null>(null);
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [connectionAttempts, setConnectionAttempts] = useState(0);

    const reconnectTimeoutRef = useRef<number | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    // queue messages when socket isn't open yet
    const messageQueue = useRef<WebSocketMessage[]>([]);
    const shouldReconnect = useRef(true);
    const maxReconnectAttempts = CONFIG.WEBSOCKET.RECONNECT_ATTEMPTS;

    const connect = useCallback(() => {
        // Clear any existing timeout
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        // Don't connect if we already have an active connection
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            console.log('WebSocket already connected');
            return;
        }

        setConnectionAttempts(prev => {
            // Don't reconnect if we've hit the max attempts
            if (prev >= maxReconnectAttempts) {
                console.log('Max reconnection attempts reached');
                setError('Unable to connect to server after multiple attempts');
                return prev;
            }

            try {
                console.log(`Connecting to WebSocket... (attempt ${prev + 1})`);
                const ws = new WebSocket(url);
                wsRef.current = ws;

                ws.onopen = () => {
                    console.log('Connected to WebSocket server');
                    setIsConnected(true);
                    setError(null);
                    setConnectionAttempts(0);
                    // Flush any queued messages
                    if (messageQueue.current.length > 0) {
                        console.log('Flushing queued messages:', messageQueue.current.map(m => m.type));
                        while (messageQueue.current.length > 0 && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                            const m = messageQueue.current.shift()!;
                            try {
                                wsRef.current.send(JSON.stringify(m));
                                if (CONFIG.DEBUG.WEBSOCKET_LOGS) console.log('Flushed queued message', m.type);
                            } catch (err) {
                                console.error('Failed to flush queued message:', err);
                                setError('Failed to send queued message');
                                // stop flushing on error
                                break;
                            }
                        }
                    }
                };

                ws.onmessage = (event) => {
                    try {
                        const message: WebSocketMessage = JSON.parse(event.data);
                        setLastMessage(message);

                        switch (message.type) {
                            case 'game_state':
                                setGameState(message.game_state);
                                break;
                            case 'error':
                                setError(message.message);
                                break;
                            case 'connected':
                            case 'game_created':
                            case 'joined_game':
                            case 'card_played':
                            case 'attack_result':
                                // Handle these in components
                                break;
                            default:
                                console.log('Unhandled message type:', message.type);
                        }
                    } catch (err) {
                        console.error('Error parsing WebSocket message:', err);
                    }
                };

                ws.onclose = (event) => {
                    console.log('WebSocket connection closed', event.code, event.reason);
                    setIsConnected(false);
                    wsRef.current = null;

                    // Only attempt to reconnect if it should reconnect and wasn't a clean close
                    if (shouldReconnect.current && event.code !== 1000) {
                        setConnectionAttempts(prevAttempts => {
                            const delay = Math.min(
                                CONFIG.WEBSOCKET.RECONNECT_DELAY_BASE * Math.pow(2, prevAttempts),
                                CONFIG.WEBSOCKET.RECONNECT_DELAY_MAX
                            );
                            console.log(`Attempting to reconnect in ${delay}ms...`);

                            reconnectTimeoutRef.current = window.setTimeout(() => {
                                if (shouldReconnect.current) {
                                    connect();
                                }
                            }, delay);

                            return prevAttempts + 1;
                        });
                    }
                };

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    setError('Connection error occurred');
                };

            } catch (err) {
                console.error('Failed to create WebSocket connection:', err);
                setError('Failed to connect to server');
            }
            return prev + 1;
        });
    }, [url]);

    const disconnect = useCallback(() => {
        shouldReconnect.current = false;

        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        if (wsRef.current) {
            wsRef.current.close(1000, 'Client disconnecting');
            wsRef.current = null;
        }

        setIsConnected(false);
    }, []);

    const sendMessage = useCallback((message: WebSocketMessage) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            try {
                wsRef.current.send(JSON.stringify(message));
                if (CONFIG.DEBUG.WEBSOCKET_LOGS) {
                    console.log('Message sent:', message.type);
                }
            } catch (err) {
                console.error('Failed to send message:', err);
                setError('Failed to send message');
            }
        } else {
            // Queue message to be sent when socket opens
            console.log('Socket not open yet, queueing message:', message.type);
            messageQueue.current.push(message);
            // Clear any previous connection error since we're retrying on open
            setError(null);
        }
    }, []);

    // Game-specific methods
    const createGame = useCallback((playerName: string, playerFaction: Faction) => {
        sendMessage({
            type: 'create_game',
            player_name: playerName,
            player_faction: playerFaction
        });
    }, [sendMessage]);

    const joinGame = useCallback((gameId: string, playerName: string, playerFaction: Faction) => {
        sendMessage({
            type: 'join_game',
            game_id: gameId,
            player_name: playerName,
            player_faction: playerFaction
        });
    }, [sendMessage]);

    // Helper to attempt joining by game ID only (useful for reconnects). Server will apply defaults
    // for player_name and player_faction if they're not provided.
    const joinGameById = useCallback((gameId: string) => {
        sendMessage({
            type: 'join_game',
            game_id: gameId
        });
    }, [sendMessage]);

    const playCard = useCallback((playerId: string, cardGameId: string, zone?: Zone) => {
        sendMessage({
            type: 'play_card',
            player_id: playerId,
            card_game_id: cardGameId,
            zone: zone
        });
    }, [sendMessage]);

    const attack = useCallback((playerId: string, attackerId: string, targetZone: Zone) => {
        sendMessage({
            type: 'attack',
            player_id: playerId,
            attacker_id: attackerId,
            target_zone: targetZone
        });
    }, [sendMessage]);

    const drawCard = useCallback((playerId: string) => {
        sendMessage({
            type: 'draw_card',
            player_id: playerId
        });
    }, [sendMessage]);

    const nextPhase = useCallback(() => {
        sendMessage({
            type: 'next_phase'
        });
    }, [sendMessage]);

    const getGameState = useCallback(() => {
        sendMessage({
            type: 'get_game_state'
        });
    }, [sendMessage]);

    const resumeSession = useCallback((gameId: string, playerId: string) => {
        sendMessage({
            type: 'resume_session',
            game_id: gameId,
            player_id: playerId
        });
    }, [sendMessage]);

    // New effect system methods
    const continueEffect = useCallback((playerId: string, effectId: string, chosenValue: any) => {
        sendMessage({
            type: 'continue_effect',
            player_id: playerId,
            effect_id: effectId,
            chosen_value: chosenValue
        });
    }, [sendMessage]);

    const getCardStats = useCallback((cardGameId: string) => {
        sendMessage({
            type: 'get_card_stats',
            card_game_id: cardGameId
        });
    }, [sendMessage]);

    useEffect(() => {
        shouldReconnect.current = true;
        connect();

        return () => {
            disconnect();
        };
    }, [url]); // Only depend on URL, not connect/disconnect to avoid infinite loops

    const reconnect = useCallback(() => {
        shouldReconnect.current = true;
        setConnectionAttempts(0);
        setError(null);
        connect();
    }, [connect]);

    return {
        isConnected,
        gameState,
        lastMessage,
        error,
        connectionAttempts,
        sendMessage,
        createGame,
        joinGame,
        joinGameById,
        resumeSession,
        playCard,
        attack,
        drawCard,
        nextPhase,
        getGameState,
        continueEffect,
        getCardStats,
        reconnect,
        disconnect
    };
};