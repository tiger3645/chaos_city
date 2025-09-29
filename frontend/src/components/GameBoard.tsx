import React from 'react';
import { GameState, Zone, Player } from '../types/game';
import Card from './Card';
import { Heart, Users, Clock, Target } from 'lucide-react';

interface GameBoardProps {
    gameState: GameState;
    currentPlayerId?: string | null;
    onPlayCard?: (cardId: string, zone?: Zone) => void;
    onAttack?: (attackerId: string, targetZone: Zone) => void;
    onNextPhase?: () => void;
    onDrawCard?: () => void;
}

const GameBoard: React.FC<GameBoardProps> = ({
    gameState,
    currentPlayerId,
    onPlayCard,
    onAttack,
    onNextPhase,
    onDrawCard
}) => {
    const currentPlayer = gameState.players.find(p => p.id === currentPlayerId);
    const opponent = gameState.players.find(p => p.id !== currentPlayerId);

    if (!currentPlayer || !opponent) {
        return <div className="text-white">Loading game...</div>;
    }

    const zones = [Zone.BRUTES, Zone.SHOOTERS, Zone.TALKERS];
    const isCurrentPlayerTurn = gameState.current_player === gameState.players.indexOf(currentPlayer);

    return (
        <div className="min-h-screen bg-chaos-dark text-white p-4">
            {/* Game Header */}
            <div className="flex justify-between items-center mb-6 bg-black/30 p-4 rounded-lg">
                <div className="flex items-center gap-4">
                    <h1 className="text-2xl font-display font-bold text-chaos-gold">
                        Ciudad del Caos
                    </h1>
                    <div className="flex items-center gap-2">
                        <Clock className="w-5 h-5" />
                        <span>Turno {gameState.turn} - {gameState.phase}</span>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    {isCurrentPlayerTurn && (
                        <button
                            onClick={onNextPhase}
                            className="px-4 py-2 bg-chaos-gold text-black font-bold rounded hover:bg-opacity-80"
                        >
                            Siguiente Fase
                        </button>
                    )}
                    {gameState.phase === 'draw' && isCurrentPlayerTurn && (
                        <button
                            onClick={onDrawCard}
                            className="px-4 py-2 bg-chaos-blue text-white font-bold rounded hover:bg-opacity-80"
                        >
                            Robar Carta
                        </button>
                    )}
                </div>
            </div>

            {/* Opponent Area */}
            <div className="mb-8">
                <div className="flex items-center gap-2 mb-4">
                    <Users className="w-5 h-5" />
                    <h2 className="text-xl font-bold">{opponent.name}</h2>
                    <div className="flex items-center gap-1 ml-4">
                        <Heart className="w-4 h-4 text-red-400" />
                        <span>{opponent.reputation}</span>
                    </div>
                    <span className="text-sm text-gray-400">
                        Cartas en mano: {opponent.hand_count} | Mazo: {opponent.deck_count}
                    </span>
                </div>

                {/* Opponent Field */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                    {zones.map(zone => (
                        <div key={zone} className="border-2 border-gray-600 rounded-lg p-4 min-h-48">
                            <h3 className="text-center font-bold mb-2 capitalize">{zone}</h3>
                            <div className="flex flex-wrap gap-2">
                                {opponent.field[zone].map((card, index) => (
                                    <Card key={`${card.id}-${index}`} card={card} />
                                ))}
                            </div>
                            {gameState.active_environments[zone] && (
                                <div className="mt-2 p-2 bg-purple-900/30 rounded border border-purple-500">
                                    <Card card={gameState.active_environments[zone]!} />
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Player Area */}
            <div>
                <div className="flex items-center gap-2 mb-4">
                    <Users className="w-5 h-5" />
                    <h2 className="text-xl font-bold">{currentPlayer.name}</h2>
                    <div className="flex items-center gap-1 ml-4">
                        <Heart className="w-4 h-4 text-red-400" />
                        <span>{currentPlayer.reputation}</span>
                    </div>
                    <span className="text-sm text-gray-400">
                        Cartas en mano: {currentPlayer.hand_count} | Mazo: {currentPlayer.deck_count}
                    </span>
                    {isCurrentPlayerTurn && (
                        <span className="ml-4 px-2 py-1 bg-green-600 text-white text-sm rounded">
                            Tu turno
                        </span>
                    )}
                </div>

                {/* Player Field */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                    {zones.map(zone => (
                        <div key={zone} className="border-2 border-gray-400 rounded-lg p-4 min-h-48">
                            <h3 className="text-center font-bold mb-2 capitalize">{zone}</h3>
                            <div className="flex flex-wrap gap-2">
                                {currentPlayer.field[zone].map((card, index) => (
                                    <Card
                                        key={`${card.id}-${index}`}
                                        card={card}
                                        onClick={() => {
                                            if (gameState.phase === 'action' && isCurrentPlayerTurn) {
                                                // Handle attack action
                                                console.log(`Attack with ${card.name}`);
                                            }
                                        }}
                                        isPlayable={gameState.phase === 'action' && isCurrentPlayerTurn}
                                    />
                                ))}
                            </div>
                            {gameState.active_environments[zone] && (
                                <div className="mt-2 p-2 bg-purple-900/30 rounded border border-purple-500">
                                    <Card card={gameState.active_environments[zone]!} />
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Hand (would be populated from websocket) */}
                <div className="mt-6 p-4 bg-black/30 rounded-lg">
                    <h3 className="font-bold mb-2">Tu mano</h3>
                    <div className="flex gap-2 overflow-x-auto">
                        {/* Hand cards would be displayed here */}
                        <div className="text-gray-400 text-center py-8">
                            Cartas en mano se mostrarán aquí
                        </div>
                    </div>
                </div>
            </div>

            {/* Game Status */}
            {gameState.winner && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
                    <div className="bg-white text-black p-8 rounded-lg text-center">
                        <h2 className="text-3xl font-bold mb-4">¡Juego Terminado!</h2>
                        <p className="text-xl">
                            Ganador: {gameState.players.find(p => p.id === gameState.winner)?.name}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GameBoard;