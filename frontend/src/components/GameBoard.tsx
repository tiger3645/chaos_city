import React from "react";
import { GameState, Zone } from "../types/game";
import Card from "./Card";
import {
  Heart,
  Users,
  Clock,
  ArrowBigRight,
  Coins,
  Layers,
} from "lucide-react";

interface GameBoardProps {
  gameState: GameState;
  currentPlayerId?: string | null;
  onNextPhase?: () => void;
  onDrawCard?: () => void;
}

const GameBoard: React.FC<GameBoardProps> = ({
  gameState,
  currentPlayerId,
  onNextPhase,
  onDrawCard,
}) => {
  if (!gameState || !gameState.players || gameState.players.length < 2) {
    return (
      <div className="min-h-screen bg-chaos-dark flex items-center justify-center">
        <div className="text-center text-white">
          <div className="animate-spin w-12 h-12 border-4 border-chaos-gold border-t-transparent rounded-full mx-auto mb-4"></div>
          <h2 className="text-xl font-bold mb-2">Esperando jugadores...</h2>
          <p className="text-gray-400">Cargando estado del juego</p>
        </div>
      </div>
    );
  }

  // Server-provided current player index
  const serverCurrentIndex = Number.isFinite(gameState.current_player)
    ? gameState.current_player
    : 0;
  const serverCurrentPlayer = gameState.players[serverCurrentIndex];

  // Determine which player object represents the local client (if any)
  const localPlayer = currentPlayerId
    ? gameState.players.find((p) => p.id === currentPlayerId) || null
    : null;

  // Use localPlayer for UI when available, otherwise show the server's current player
  const currentPlayer = localPlayer || serverCurrentPlayer || null;

  const opponent = gameState.players.find((p) => p.id !== currentPlayer?.id);

  if (!currentPlayer) {
    return (
      <div className="min-h-screen bg-chaos-dark flex items-center justify-center">
        <div className="text-center text-white">
          <h2 className="text-xl font-bold mb-2">
            Error: Jugador no encontrado
          </h2>
          <p className="text-gray-400">Player ID: {currentPlayerId}</p>
          <p className="text-gray-400">
            Available players: {gameState.players.map((p) => p.id).join(", ")}
          </p>
        </div>
      </div>
    );
  }

  if (!opponent) {
    return (
      <div className="min-h-screen bg-chaos-dark flex items-center justify-center">
        <div className="text-center text-white">
          <h2 className="text-xl font-bold mb-2">Esperando oponente...</h2>
          <p className="text-gray-400">
            El juego comenzará cuando se una el segundo jugador
          </p>
        </div>
      </div>
    );
  }

  const zones = [Zone.FIGHTER, Zone.GUNSINGER, Zone.TALKER];
  // The turn belongs to whoever is at gameState.current_player. Only consider it
  // "Tu turno" when the local player's id matches that server index.
  const isCurrentPlayerTurn =
    !!localPlayer &&
    serverCurrentPlayer &&
    localPlayer.id === serverCurrentPlayer.id;

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
            <span>
              Turno {gameState.turn} - {gameState.phase}
            </span>
            <Coins className="w-4 h-4 text-yellow-400 ml-2" />
            <span>{gameState.available_coins}</span>
          </div>
        </div>
      </div>

      {/* Opponent Area */}
      <div className="mb-8">
        <div className="flex items-center justify-end gap-2 mb-4">
          <div>
            <div className="flex items-center justify-end gap-2 mb-2">
              <Users className="w-5 h-5" />
              <h2 className="text-xl font-bold">{opponent.name}</h2>
            </div>
            <div className="flex items-center gap-1">
              <Heart className="w-4 h-4 text-red-400" />
              <span>{opponent.reputation}</span>

              <Coins className="w-4 h-4 text-yellow-400 ml-2" />
              <span>{opponent.coins}</span>

              <Layers className="w-4 h-4 text-gray-400 ml-2" />
              {opponent.deck_count}
            </div>
          </div>
        </div>

        {/* Opponent Field */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          {zones.map((zone) => (
            <div
              key={zone}
              className="border-2 border-gray-600 rounded-lg p-4 min-h-48"
            >
              <h3 className="text-center font-bold mb-2 capitalize">{zone}</h3>
              <div className="flex flex-wrap gap-2">
                {opponent.field[zone].map((card, index) => (
                  <Card key={`${card.id}-${index}`} card={card} />
                ))}
              </div>
              {gameState.active_environment_card && (
                <div className="mt-2 p-2 bg-purple-900/30 rounded border border-purple-500">
                  <Card card={gameState.active_environment_card} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Player Area */}
      <div>
        <div className="flex items-center gap-2 mb-4 justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-5 h-5" />
              <h2 className="text-xl font-bold">{currentPlayer.name}</h2>
              {isCurrentPlayerTurn && (
                <span className="ml-4 px-2 py-1 bg-green-600 text-white text-sm rounded">
                  Tu turno
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              <Heart className="w-4 h-4 text-red-400" />
              <span>{currentPlayer.reputation}</span>

              <Coins className="w-4 h-4 text-yellow-400 ml-2" />
              <span>{currentPlayer.coins}</span>

              <Layers className="w-4 h-4 text-gray-400 ml-2" />
              {currentPlayer.deck_count}
            </div>
          </div>
          <div className="flex items-center gap-4 flex-1 justify-end">
            {gameState.phase !== "draw" && isCurrentPlayerTurn && (
              <button
                onClick={onNextPhase}
                className="px-4 py-2 bg-chaos-gold text-black font-bold rounded hover:opacity-80 active:opacity-100 cursor-pointer flex"
              >
                Siguiente Fase
                <ArrowBigRight className="ms-2" />
              </button>
            )}
            {gameState.phase === "draw" && isCurrentPlayerTurn && (
              <button
                onClick={onDrawCard}
                className="px-4 py-2 bg-chaos-blue text-white font-bold rounded hover:opacity-80 active:opacity-100 cursor-pointer flex items-center"
              >
                Robar Carta
                <Layers className="inline w-4 h-4 mr-1 ml-3" />
                {currentPlayer.deck_count}
              </button>
            )}
          </div>
        </div>

        {/* Player Field */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          {zones.map((zone) => (
            <div
              key={zone}
              className="border-2 border-gray-400 rounded-lg p-4 min-h-48"
            >
              <h3 className="text-center font-bold mb-2 capitalize">{zone}</h3>
              <div className="flex flex-wrap gap-2">
                {currentPlayer.field[zone].map((card, index) => (
                  <Card
                    key={`${card.id}-${index}`}
                    card={card}
                    onClick={() => {
                      if (gameState.phase === "action" && isCurrentPlayerTurn) {
                        // Handle attack action
                        console.log(`Attack with ${card.name}`);
                      }
                    }}
                    isPlayable={
                      gameState.phase === "action" && isCurrentPlayerTurn
                    }
                  />
                ))}
              </div>
              {gameState.active_environment_card && (
                <div className="mt-2 p-2 bg-purple-900/30 rounded border border-purple-500">
                  <Card card={gameState.active_environment_card} />
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-black/30 rounded-lg">
          <h3 className="font-bold mb-2">Tu mano</h3>
          <div className="text-gray-400 text-center py-8 flex flex-row flex-wrap justify-center gap-2">
            {currentPlayer.hand_cards.map((card) => (
              <Card key={card.id} card={card} />
            ))}
          </div>
        </div>
      </div>

      {/* Game Status */}
      {gameState.winner && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white text-black p-8 rounded-lg text-center">
            <h2 className="text-3xl font-bold mb-4">¡Juego Terminado!</h2>
            <p className="text-xl">
              Ganador:{" "}
              {gameState.players.find((p) => p.id === gameState.winner)?.name}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default GameBoard;
