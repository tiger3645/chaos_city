import React, { useState } from "react";
import { GameState, Zone } from "../types/game";
import { CardStats } from "../types/effects";
import Card from "./Card";
import ConnectionStatus from "./ConnectionStatus";
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
  onPlayCard?: (cardGameId: string) => void;
  requestCardStats?: (cardGameId: string) => void;
  getCachedCardStats?: (cardGameId: string) => CardStats | undefined;
  isConnected?: boolean;
  error?: string | null;
  connectionAttempts?: number;
  onReconnect?: () => void;
  lastAction?: string | null;
  gameId?: string | null;
}

const GameBoard: React.FC<GameBoardProps> = ({
  gameState,
  currentPlayerId,
  onNextPhase,
  onDrawCard,
  onPlayCard,
  requestCardStats,
  getCachedCardStats,
  isConnected,
  error,
  connectionAttempts,
  onReconnect,
  lastAction,
  gameId,
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

  // Estado para la carta seleccionada
  const [selectedCardGameId, setSelectedCardGameId] = useState<string | null>(
    null
  );

  // Handler para seleccionar/deseleccionar carta
  const handleCardClick = (cardGameId: string) => {
    if (selectedCardGameId === cardGameId) {
      // Deseleccionar si ya está seleccionada
      setSelectedCardGameId(null);
    } else {
      // Seleccionar nueva carta
      setSelectedCardGameId(cardGameId);
    }
  };

  // Handler para jugar carta seleccionada
  const handlePlayCard = () => {
    if (selectedCardGameId && onPlayCard) {
      onPlayCard(selectedCardGameId);
      setSelectedCardGameId(null); // Deseleccionar después de jugar
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-stone-900 via-stone-800 to-stone-900 text-white overflow-hidden relative">
      {/* Background texture overlay */}
      <div className="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] pointer-events-none" />

      {/* Top Header Bar */}
      <div className="relative z-10 flex justify-between items-center px-6 py-3 bg-gradient-to-r from-amber-950/80 via-amber-900/60 to-amber-950/80 border-b-2 border-amber-700/50 shadow-2xl">
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-display font-bold text-amber-400 drop-shadow-lg">
            Ciudad del Caos
          </h1>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1 bg-black/40 px-3 py-1 rounded-lg border border-amber-700/30">
              <Clock className="w-4 h-4 text-amber-400" />
              <span className="text-gray-200">Turno {gameState.turn}</span>
            </div>
            <div className="flex items-center gap-1 bg-black/40 px-3 py-1 rounded-lg border border-amber-700/30">
              <span className="text-amber-400 font-semibold">
                {gameState.phase}
              </span>
            </div>
            <div className="flex items-center gap-1 bg-black/40 px-3 py-1 rounded-lg border border-amber-700/30">
              <Coins className="w-4 h-4 text-yellow-400" />
              <span className="text-gray-200">{gameState.available_coins}</span>
            </div>
          </div>
        </div>
        <div
          className="flex items-center flex-col cursor-pointer"
          onClick={() => {
            navigator.clipboard.writeText(gameId || "");
          }}
        >
          <ConnectionStatus
            isConnected={isConnected || false}
            error={error || null}
            connectionAttempts={connectionAttempts || 0}
            onReconnect={onReconnect || (() => {})}
            lastAction={lastAction || null}
            gameId={gameId || null}
          />
          {gameId && (
            <div className="text-xs text-amber-300 mt-1 font-mono">
              Game ID: {gameId}
            </div>
          )}
        </div>
      </div>

      {/* Main Game Board */}
      <div className="flex h-[calc(100vh-60px)]">
        {/* Left Player Info Panel */}
        <div className="w-48 bg-gradient-to-b from-stone-900/95 to-stone-950/95 border-r-2 border-amber-700/30 p-4 flex flex-col justify-start">
          <div className="bg-black/40 rounded-lg p-3 border border-red-900/50 shadow-lg">
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-5 h-5 text-red-400" />
              <h2 className="text-lg font-bold text-red-300">
                {opponent.name}
              </h2>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between bg-black/30 px-2 py-1 rounded">
                <div className="flex items-center gap-1">
                  <Heart className="w-4 h-4 text-red-400" />
                  <span className="text-gray-300">Vida</span>
                </div>
                <span className="font-bold text-red-300">
                  {opponent.reputation}
                </span>
              </div>
              <div className="flex items-center justify-between bg-black/30 px-2 py-1 rounded">
                <div className="flex items-center gap-1">
                  <Coins className="w-4 h-4 text-yellow-400" />
                  <span className="text-gray-300">Coins</span>
                </div>
                <span className="font-bold text-yellow-300">
                  {opponent.coins}
                </span>
              </div>
              <div className="flex items-center justify-between bg-black/30 px-2 py-1 rounded">
                <div className="flex items-center gap-1">
                  <Layers className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-300">Mazo</span>
                </div>
                <span className="font-bold text-gray-200">
                  {opponent.deck_count}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Center Board Area */}
        <div className="flex-1 flex flex-col relative">
          {/* Opponent Field */}
          <div className="flex-1 flex flex-col justify-start p-2 pt-4">
            {zones
              .slice()
              .reverse()
              .map((zone) => (
                <div
                  key={zone}
                  className="mb-1 bg-gradient-to-r from-stone-800/60 via-stone-700/80 to-stone-800/60 rounded border border-amber-800/40 shadow-inner backdrop-blur-sm"
                  style={{
                    minHeight: "100px",
                    maxHeight: "120px",
                  }}
                >
                  <div className="flex items-center h-full px-3 py-1 row">
                    {/* Zone Label */}
                    <div className="w-20 flex items-center justify-center">
                      <span className="text-xs font-bold text-amber-600/80 uppercase tracking-wider transform -rotate-180 writing-mode-vertical">
                        {zone}
                      </span>
                    </div>
                    {/* Cards Container */}
                    <div className="flex-1 flex items-center gap-1 overflow-x-auto px-2">
                      {opponent.field[zone].map((card, index) => (
                        <div
                          key={`${card.id}-${index}`}
                          className="flex-shrink-0"
                        >
                          <Card card={card} />
                        </div>
                      ))}
                      {opponent.field[zone].length === 0 && (
                        <div className="flex-1 flex items-center justify-center text-gray-600 text-sm italic">
                          Fila vacía
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
          </div>

          {/* Center Divider */}
          <div className="h-0.5 bg-gradient-to-r from-transparent via-amber-600 to-transparent shadow-lg" />
          <div className="h-8 bg-gradient-to-b from-amber-900/20 to-amber-950/20 flex items-center justify-center border-y border-amber-700/20">
            <div className="text-xs text-amber-500/60 font-bold uppercase tracking-widest">
              Línea de Batalla
            </div>
          </div>
          <div className="h-0.5 bg-gradient-to-r from-transparent via-amber-600 to-transparent shadow-lg" />

          {/* Player Field */}
          <div className="flex-1 flex flex-col justify-end p-2 pb-4">
            {zones.map((zone) => (
              <div
                key={zone}
                className="mb-1 bg-gradient-to-r from-stone-800/60 via-stone-700/80 to-stone-800/60 rounded border border-amber-800/40 shadow-inner backdrop-blur-sm"
                style={{
                  minHeight: "100px",
                  maxHeight: "120px",
                }}
              >
                <div className="flex items-center h-full px-3 py-1 row">
                  {/* Zone Label */}
                  <div className="w-20 flex items-center justify-center">
                    <span className="text-xs font-bold text-amber-600/80 uppercase tracking-wider writing-mode-vertical">
                      {zone}
                    </span>
                  </div>
                  {/* Cards Container */}
                  <div className="flex-1 flex items-center gap-1 overflow-x-auto py-2 px-2">
                    {currentPlayer.field[zone].map((card, index) => (
                      <div
                        key={`${card.id}-${index}`}
                        className="flex-shrink-0"
                      >
                        <Card
                          card={card}
                          onClick={() => {
                            if (
                              gameState.phase === "action" &&
                              isCurrentPlayerTurn
                            ) {
                              console.log(`Attack with ${card.name}`);
                            }
                          }}
                          isPlayable={
                            gameState.phase === "action" && isCurrentPlayerTurn
                          }
                          effectiveStats={getCachedCardStats?.(card.game_id)}
                          onHover={() => requestCardStats?.(card.game_id)}
                        />
                      </div>
                    ))}
                    {currentPlayer.field[zone].length === 0 && (
                      <div className="flex-1 flex items-center justify-center text-gray-600 text-sm italic">
                        Fila vacía
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Player Info Panel */}
        <div className="w-48 bg-gradient-to-b from-stone-900/95 to-stone-950/95 border-l-2 border-amber-700/30 p-4 flex flex-col justify-end">
          <div className="bg-black/40 rounded-lg p-3 border border-blue-900/50 shadow-lg mb-4">
            <div className="flex items-center gap-2 mb-3">
              <Users className="w-5 h-5 text-blue-400" />
              <h2 className="text-lg font-bold text-blue-300">
                {currentPlayer.name}
              </h2>
            </div>
            {isCurrentPlayerTurn && (
              <div className="mb-3 px-2 py-1 bg-green-600/80 text-white text-xs rounded text-center font-bold">
                ⚡ TU TURNO
              </div>
            )}
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between bg-black/30 px-2 py-1 rounded">
                <div className="flex items-center gap-1">
                  <Heart className="w-4 h-4 text-red-400" />
                  <span className="text-gray-300">Vida</span>
                </div>
                <span className="font-bold text-red-300">
                  {currentPlayer.reputation}
                </span>
              </div>
              <div className="flex items-center justify-between bg-black/30 px-2 py-1 rounded">
                <div className="flex items-center gap-1">
                  <Coins className="w-4 h-4 text-yellow-400" />
                  <span className="text-gray-300">Coins</span>
                </div>
                <span className="font-bold text-yellow-300">
                  {currentPlayer.coins}
                </span>
              </div>
              <div className="flex items-center justify-between bg-black/30 px-2 py-1 rounded">
                <div className="flex items-center gap-1">
                  <Layers className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-300">Mazo</span>
                </div>
                <span className="font-bold text-gray-200">
                  {currentPlayer.deck_count}
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-2">
            {gameState.phase === "draw" && isCurrentPlayerTurn && (
              <button
                onClick={onDrawCard}
                className="w-full px-3 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold rounded-lg hover:from-blue-500 hover:to-blue-600 active:from-blue-700 active:to-blue-800 shadow-lg flex items-center justify-center gap-2 text-sm"
              >
                <Layers className="w-4 h-4" />
                Robar Carta
              </button>
            )}
            {gameState.phase !== "draw" && isCurrentPlayerTurn && (
              <button
                onClick={onNextPhase}
                className="w-full px-3 py-2 bg-gradient-to-r from-amber-600 to-amber-700 text-black font-bold rounded-lg hover:from-amber-500 hover:to-amber-600 active:from-amber-700 active:to-amber-800 shadow-lg flex items-center justify-center gap-2 text-sm"
              >
                Siguiente Fase
                <ArrowBigRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Hand Area - Fixed Overlay */}
      <div className="fixed mx-48 bottom-0 left-0 right-0 z-20 bg-gradient-to-t from-black/95 via-stone-900/90 to-transparent border-t-2 border-amber-700/40 shadow-2xl backdrop-blur-sm">
        <div className="px-4 py-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider">
              Tu Mano
            </h3>
            <span className="text-xs text-gray-400">
              {currentPlayer.hand_cards.length} cartas
            </span>
          </div>
          <div
            className="flex justify-center items-center gap-2 pb-2 overflow-visible"
            style={{ minHeight: "110px" }}
          >
            {currentPlayer.hand_cards.map((card) => {
              const isSelected = selectedCardGameId === card.game_id;
              const canPlayCard =
                gameState.phase === "deploy" && isCurrentPlayerTurn;

              return (
                <div key={card.game_id} className="relative flex-shrink-0 z-10">
                  <Card
                    card={card}
                    onClick={() => canPlayCard && handleCardClick(card.game_id)}
                    isPlayable={canPlayCard}
                    isSelected={isSelected}
                  />
                  {isSelected && canPlayCard && (
                    <button
                      onClick={handlePlayCard}
                      className="absolute -right-2 top-1/2 transform -translate-y-1/2 translate-x-full px-3 py-2 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 active:bg-green-800 shadow-xl z-10 text-sm whitespace-nowrap"
                    >
                      ▶ Jugar
                    </button>
                  )}
                </div>
              );
            })}
            {currentPlayer.hand_cards.length === 0 && (
              <div className="text-gray-500 text-sm italic">Mano vacía</div>
            )}
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
