import { useState, useEffect, useRef } from "react";
import { useWebSocket } from "./hooks/useWebSocket";
import { useGameSession } from "./hooks/useGameSession";
import { useEffects } from "./hooks/useEffects";
import { Faction } from "./types/game";
import GameSetup from "./components/GameSetup";
import GameBoard from "./components/GameBoard";
import EffectModal from "./components/EffectModal";
import RevealedInfoModal from "./components/RevealedInfoModal";
import { EffectNotificationsContainer } from "./components/EffectNotification";
import { CONFIG } from "./config";

function App() {
  const { session, saveSession, clearSession } = useGameSession();

  const [currentView, setCurrentView] = useState<"setup" | "game">(
    session?.view === "game" ? "game" : "setup"
  );
  const [currentPlayerId, setCurrentPlayerId] = useState<string | null>(
    session?.playerId || null
  );
  const [currentGameId, setCurrentGameId] = useState<string | null>(
    session?.gameId || null
  );

  // UX states
  const [isResuming, setIsResuming] = useState(false);
  const [lastAction, setLastAction] = useState<string | null>(null);

  const {
    isConnected,
    gameState,
    lastMessage,
    error,
    connectionAttempts,
    createGame,
    joinGame,
    joinGameById,
    resumeSession,
    playCard,
    drawCard,
    nextPhase,
    continueEffect,
    getCardStats,
    reconnect,
  } = useWebSocket(CONFIG.WEBSOCKET.URL);

  // Effects system
  const {
    effectModalOpen,
    effectMessage,
    effectChoices,
    handleEffectChoice,
    handleCancelEffect,
    revealedInfoModalOpen,
    revealedInfo,
    closeRevealedInfoModal,
    requestCardStats,
    getCachedCardStats,
    notifications,
    dismissNotification,
  } = useEffects(lastMessage, continueEffect, getCardStats);

  // Track whether we've attempted to resume/join for the saved session to avoid races
  const resumeAttemptRef = useRef<string>("");

  // Handle incoming messages
  useEffect(() => {
    if (!lastMessage) return;

    switch (lastMessage.type) {
      case "game_created": {
        const gameId = lastMessage.game_id;
        const playerId = lastMessage.player_id;
        if (gameId) {
          setCurrentGameId(gameId);
          setCurrentView("game");
          // clear create indicators
          setLastAction(null);
          if (playerId) {
            setCurrentPlayerId(playerId);
            saveSession(gameId, playerId, "game");
          }
        }
        break;
      }
      case "joined_game": {
        const joinedGameId = lastMessage.game_id;
        const playerId = lastMessage.player_id;
        if (joinedGameId) {
          setCurrentGameId(joinedGameId);
          setCurrentView("game");
          // clear join indicators
          setLastAction(null);
          if (playerId) {
            setCurrentPlayerId(playerId);
            saveSession(joinedGameId, playerId, "game");
          }
        }
        break;
      }
      case "resumed_session": {
        const gameId = lastMessage.game_id;
        const playerId = lastMessage.player_id;
        if (gameId) {
          setCurrentGameId(gameId);
          setIsResuming(false);
          setLastAction(null);
          setCurrentView("game");
          if (playerId) {
            setCurrentPlayerId(playerId);
            saveSession(gameId, playerId, "game");
          }
        }
        break;
      }
      case "game_state": {
        // clear transient states when receiving an update
        setIsResuming(false);
        setLastAction(null);
        break;
      }
      case "error": {
        console.error("Game error:", lastMessage.message);
        alert(`Error: ${lastMessage.message}`);
        // clear pending UX states
        setIsResuming(false);
        setLastAction(null);
        break;
      }
      default:
        break;
    }
  }, [lastMessage, saveSession]);

  // Assign playerId fallback if not known and only one player exists
  useEffect(() => {
    if (gameState && currentView === "game" && currentGameId) {
      if (!currentPlayerId && gameState.players?.length === 1) {
        const playerId = gameState.players[0].id;
        setCurrentPlayerId(playerId);
        saveSession(currentGameId, playerId, "game");
      } else if (currentPlayerId && currentGameId) {
        saveSession(currentGameId, currentPlayerId, "game");
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameState, currentView, currentGameId, currentPlayerId]);

  // Reconnect/resume saved session
  useEffect(() => {
    if (!isConnected || !session || !session.gameId) return;

    // If we already have a gameState, no need to resume
    if (gameState) return;

    const attemptKey = `${session.gameId}:${session.playerId || ""}`;
    if (resumeAttemptRef.current === attemptKey) return;

    resumeAttemptRef.current = attemptKey;

    if (session.playerId) {
      setIsResuming(true);
      setLastAction("resume_session");
      console.log(
        "Attempting resumeSession for",
        session.gameId,
        session.playerId
      );
      resumeSession(session.gameId, session.playerId);
    } else if (typeof joinGameById === "function") {
      setLastAction("join_game");
      console.log("Attempting joinGameById for", session.gameId);
      joinGameById(session.gameId);
    } else {
      setLastAction("join_game");
      console.log("Attempting full join fallback for", session.gameId);
      joinGame(session.gameId, "Reconnector", Faction.POLICE);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isConnected, session?.gameId, session?.playerId, gameState]);

  const handleCreateGame = (playerName: string, playerFaction: Faction) => {
    setLastAction("create_game");
    createGame(playerName, playerFaction);
  };

  const handleJoinGame = (
    gameId: string,
    playerName: string,
    playerFaction: Faction
  ) => {
    setLastAction("join_game");
    joinGame(gameId, playerName, playerFaction);
  };

  const handleDrawCard = () => {
    if (currentPlayerId) {
      drawCard(currentPlayerId);
    }
  };

  const handlePlayCard = (cardGameId: string) => {
    if (currentPlayerId) {
      playCard(currentPlayerId, cardGameId);
    }
  };

  const handleNewGame = () => {
    clearSession();
    setCurrentView("setup");
    setCurrentPlayerId(null);
    setCurrentGameId(null);
  };

  return (
    <div className="App relative">
      {/* Effect Modals */}
      <EffectModal
        isOpen={effectModalOpen}
        message={effectMessage}
        choices={effectChoices}
        onChoose={handleEffectChoice}
        onCancel={handleCancelEffect}
      />

      <RevealedInfoModal
        isOpen={revealedInfoModalOpen}
        revealedInfo={revealedInfo}
        onClose={closeRevealedInfoModal}
      />

      {/* Notifications */}
      <EffectNotificationsContainer
        notifications={notifications}
        onDismiss={dismissNotification}
      />

      {/* Resuming banner */}
      {isResuming && (
        <div className="fixed inset-0 flex items-center justify-center z-40 pointer-events-none">
          <div className="bg-black/70 text-white px-6 py-4 rounded-lg pointer-events-auto">
            <div className="flex items-center gap-3">
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              <div>
                <div className="font-bold">Reanudando sesión...</div>
                {currentGameId && (
                  <div className="text-xs font-mono">Game: {currentGameId}</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="min-h-screen">
        {currentView === "setup" ? (
          <GameSetup
            onCreateGame={handleCreateGame}
            onJoinGame={handleJoinGame}
            isConnected={isConnected}
          />
        ) : gameState && currentPlayerId ? (
          <GameBoard
            gameState={gameState}
            currentPlayerId={currentPlayerId!}
            onNextPhase={nextPhase}
            onDrawCard={handleDrawCard}
            onPlayCard={handlePlayCard}
            requestCardStats={requestCardStats}
            getCachedCardStats={getCachedCardStats}
            isConnected={isConnected}
            error={error}
            connectionAttempts={connectionAttempts}
            onReconnect={reconnect}
            lastAction={lastAction}
            gameId={currentGameId}
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
        )}
      </div>
    </div>
  );
}

export default App;
