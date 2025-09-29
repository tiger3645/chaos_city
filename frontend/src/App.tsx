import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { useGameSession } from './hooks/useGameSession';
import { Faction, Zone } from './types/game';
import GameSetup from './components/GameSetup';
import GameBoard from './components/GameBoard';
import ConnectionStatus from './components/ConnectionStatus';
import { CONFIG } from './config';

function App() {
    const { session, saveSession, clearSession } = useGameSession();

    const [currentView, setCurrentView] = useState<'setup' | 'game'>(
        session?.view === 'game' ? 'game' : 'setup'
    );
    const [currentPlayerId, setCurrentPlayerId] = useState<string | null>(
        session?.playerId || null
    );
    const [currentGameId, setCurrentGameId] = useState<string | null>(
        session?.gameId || null
    );

    const {
        isConnected,
        gameState,
        lastMessage,
        error,
        connectionAttempts,
        createGame,
        joinGame,
        playCard,
        attack,
        drawCard,
        nextPhase,
        reconnect
    } = useWebSocket(CONFIG.WEBSOCKET.URL);
    // Efecto para manejar mensajes WebSocket
    useEffect(() => {
        if (lastMessage) {
            console.log('Received message:', lastMessage.type, lastMessage);
            console.log('Current gameState:', gameState);

            switch (lastMessage.type) {
                case 'game_created':
                    const gameId = lastMessage.game_id;
                    if (gameId) {
                        console.log('Game created, ID:', gameId);
                        setCurrentGameId(gameId);
                        setCurrentView('game');
                        // El gameState llegará después, así que esperamos a procesarlo en el otro useEffect
                    }
                    break;
                case 'joined_game':
                    const joinedGameId = lastMessage.game_id;
                    if (joinedGameId) {
                        console.log('Game joined, ID:', joinedGameId);
                        setCurrentGameId(joinedGameId);
                        setCurrentView('game');
                        // El gameState llegará después, así que esperamos a procesarlo en el otro useEffect
                    }
                    break;
                case 'game_state':
                    // Manejar actualizaciones de estado del juego
                    console.log('Game state updated');
                    break;
                case 'error':
                    console.error('Game error:', lastMessage.message);
                    alert(`Error: ${lastMessage.message}`);
                    break;
            }
        }
    }, [lastMessage]);

    // Efecto separado para manejar cambios en el gameState
    useEffect(() => {
        if (gameState && currentView === 'game' && currentGameId) {
            console.log('Processing gameState with players:', gameState.players?.map(p => p.id));

            // Si tenemos un gameState pero no un playerId, asignarlo
            if (!currentPlayerId && gameState.players?.length > 0) {
                // Asignar el primer jugador disponible
                const playerId = gameState.players[0].id;
                console.log('Assigning player ID:', playerId);
                setCurrentPlayerId(playerId);
                saveSession(currentGameId, playerId, 'game');
            } else if (currentPlayerId && currentGameId) {
                // Actualizar la sesión con los datos actuales
                saveSession(currentGameId, currentPlayerId, 'game');
            }
        }
    }, [gameState, currentView, currentGameId]);

    // Efecto para reconectar a juego guardado
    useEffect(() => {
        if (isConnected && session && session.gameId && !gameState) {
            console.log('Attempting to rejoin saved game:', session.gameId);
            joinGame(session.gameId);
        }
    }, [isConnected, session]);

    const handleCreateGame = (playerName: string, playerFaction: Faction) => {
        createGame(playerName, playerFaction);
    };

    const handleJoinGame = (gameId: string, playerName: string, playerFaction: Faction) => {
        joinGame(gameId, playerName, playerFaction);
    };

    const handlePlayCard = (cardId: string, zone?: Zone) => {
        if (currentPlayerId) {
            playCard(currentPlayerId, cardId, zone);
        }
    };

    const handleAttack = (attackerId: string, targetZone: Zone) => {
        if (currentPlayerId) {
            attack(currentPlayerId, attackerId, targetZone);
        }
    };

    const handleDrawCard = () => {
        if (currentPlayerId) {
            drawCard(currentPlayerId);
        }
    };

    const handleNewGame = () => {
        clearSession();
        setCurrentView('setup');
        setCurrentPlayerId(null);
        setCurrentGameId(null);
    };

    return (
        <div className="App relative">
            {/* Connection Status - Fixed en esquina superior derecha */}
            <div className="fixed top-4 right-4 z-50">
                <div className="bg-black/90 border border-gray-600 rounded-lg p-3 shadow-lg">
                    <ConnectionStatus
                        isConnected={isConnected}
                        error={error}
                        connectionAttempts={connectionAttempts}
                        onReconnect={reconnect}
                    />
                    {currentGameId && (
                        <div className="text-xs text-blue-300 mt-2 font-mono">
                            Game ID: {currentGameId}
                        </div>
                    )}
                    <div className="text-xs text-gray-500 mt-1">
                        {CONFIG.WEBSOCKET.URL}
                    </div>
                </div>
            </div>

            {/* Botón Nuevo Juego en juegos activos */}
            {currentView === 'game' && (
                <div className="fixed top-4 left-4 z-40">
                    <button
                        onClick={handleNewGame}
                        className="bg-chaos-red text-white px-3 py-1 rounded text-sm font-bold hover:bg-opacity-80 transition-colors"
                    >
                        Nuevo Juego
                    </button>
                </div>
            )}

            <div className="min-h-screen">
                {currentView === 'setup' ? (
                    <GameSetup
                        onCreateGame={handleCreateGame}
                        onJoinGame={handleJoinGame}
                        isConnected={isConnected}
                    />
                ) : (
                    gameState && currentPlayerId ? (
                        <GameBoard
                            gameState={gameState}
                            currentPlayerId={currentPlayerId}
                            gameId={currentGameId || undefined}
                            onPlayCard={handlePlayCard}
                            onAttack={handleAttack}
                            onNextPhase={nextPhase}
                            onDrawCard={handleDrawCard}
                        />
                    ) : (
                        <div className="min-h-screen bg-chaos-dark flex items-center justify-center">
                            <div className="text-center text-white">
                                <div className="animate-spin w-12 h-12 border-4 border-chaos-gold border-t-transparent rounded-full mx-auto mb-4"></div>
                                <h2 className="text-xl font-bold mb-2">Cargando juego...</h2>
                                <p className="text-gray-400">Game ID: {currentGameId}</p>
                                <p className="text-gray-400">Player ID: {currentPlayerId}</p>
                                <button
                                    onClick={handleNewGame}
                                    className="mt-4 px-4 py-2 bg-chaos-blue text-white rounded hover:bg-opacity-80"
                                >
                                    Cancelar y crear nuevo juego
                                </button>
                            </div>
                        </div>
                    )
                )}
            </div>
        </div>
    );
}

export default App;