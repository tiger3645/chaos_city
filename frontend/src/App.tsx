import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { Faction, Zone } from './types/game';
import GameSetup from './components/GameSetup';
import GameBoard from './components/GameBoard';
import ConnectionStatus from './components/ConnectionStatus';
import { CONFIG } from './config';

function App() {
    const [currentView, setCurrentView] = useState<'setup' | 'game'>('setup');
    const [currentPlayerId, setCurrentPlayerId] = useState<string | null>(null);

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
    useEffect(() => {
        if (lastMessage) {
            switch (lastMessage.type) {
                case 'game_created':
                case 'joined_game':
                    setCurrentView('game');
                    // In a real app, you'd get the player ID from authentication
                    // For now, we'll use the first player
                    if (gameState?.players?.[0]) {
                        setCurrentPlayerId(gameState.players[0].id);
                    }
                    break;
                case 'error':
                    console.error('Game error:', lastMessage.message);
                    alert(`Error: ${lastMessage.message}`);
                    break;
            }
        }
    }, [lastMessage, gameState]);

    const handleCreateGame = (
        player1Name: string,
        player1Faction: Faction,
        player2Name: string,
        player2Faction: Faction
    ) => {
        createGame(player1Name, player1Faction, player2Name, player2Faction);
    };

    const handleJoinGame = (gameId: string) => {
        joinGame(gameId);
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

    return (
        <div className="App">
            {/* Connection Status Bar */}
            <div className="fixed top-0 left-0 right-0 bg-black/80 p-2 z-50 flex justify-between items-center">
                <ConnectionStatus
                    isConnected={isConnected}
                    error={error}
                    connectionAttempts={connectionAttempts}
                    onReconnect={reconnect}
                />
                <div className="text-xs text-gray-400">
                    {CONFIG.WEBSOCKET.URL}
                </div>
            </div>

            <div className="pt-12">
                {currentView === 'setup' ? (
                    <GameSetup
                        onCreateGame={handleCreateGame}
                        onJoinGame={handleJoinGame}
                        isConnected={isConnected}
                    />
                ) : (
                    gameState && (
                        <GameBoard
                            gameState={gameState}
                            currentPlayerId={currentPlayerId}
                            onPlayCard={handlePlayCard}
                            onAttack={handleAttack}
                            onNextPhase={nextPhase}
                            onDrawCard={handleDrawCard}
                        />
                    )
                )}
            </div>
        </div>
    );
}

export default App;