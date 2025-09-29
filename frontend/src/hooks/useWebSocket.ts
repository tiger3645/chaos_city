import { useState, useEffect, useCallback, useRef } from 'react';
import { GameState, WebSocketMessage, AttackResult, Faction, Zone } from '../types/game';
import { CONFIG } from '../config';

export const useWebSocket = (url: string) => {
    const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
    const [isConnected, setIsConnected] = useState(false);
    const [gameState, setGameState] = useState<GameState | null>(null);
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [connectionAttempts, setConnectionAttempts] = useState(0);

    const reconnectTimeoutRef = useRef<number | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
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

        // Don't reconnect if we've hit the max attempts
        if (connectionAttempts >= maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            setError('Unable to connect to server after multiple attempts');
            return;
        }

        try {
            console.log(`Connecting to WebSocket... (attempt ${connectionAttempts + 1})`);
            const ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('Connected to WebSocket server');
                setIsConnected(true);
                setError(null);
                setConnectionAttempts(0);
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
                    const delay = Math.min(
                        CONFIG.WEBSOCKET.RECONNECT_DELAY_BASE * Math.pow(2, connectionAttempts),
                        CONFIG.WEBSOCKET.RECONNECT_DELAY_MAX
                    );
                    console.log(`Attempting to reconnect in ${delay}ms...`);

                    setConnectionAttempts(prev => prev + 1);

                    reconnectTimeoutRef.current = window.setTimeout(() => {
                        if (shouldReconnect.current) {
                            connect();
                        }
                    }, delay);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setError('Connection error occurred');
            };

        } catch (err) {
            console.error('Failed to create WebSocket connection:', err);
            setError('Failed to connect to server');
            setConnectionAttempts(prev => prev + 1);
        }
    }, [url, connectionAttempts]);

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
            console.error('WebSocket is not connected, current state:', wsRef.current?.readyState);
            setError('Not connected to server');
        }
    }, []);

    // Game-specific methods
    const createGame = useCallback((
        player1Name: string,
        player1Faction: Faction,
        player2Name: string,
        player2Faction: Faction
    ) => {
        sendMessage({
            type: 'create_game',
            player1_name: player1Name,
            player1_faction: player1Faction,
            player2_name: player2Name,
            player2_faction: player2Faction
        });
    }, [sendMessage]);

    const joinGame = useCallback((gameId: string) => {
        sendMessage({
            type: 'join_game',
            game_id: gameId
        });
    }, [sendMessage]);

    const playCard = useCallback((playerId: string, cardId: string, zone?: Zone) => {
        sendMessage({
            type: 'play_card',
            player_id: playerId,
            card_id: cardId,
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
        playCard,
        attack,
        drawCard,
        nextPhase,
        getGameState,
        reconnect,
        disconnect
    };
};