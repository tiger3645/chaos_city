import React from "react";
import { Wifi, WifiOff, RotateCcw, AlertCircle } from "lucide-react";

interface ConnectionStatusProps {
  isConnected: boolean;
  error: string | null;
  connectionAttempts?: number;
  onReconnect?: () => void;
  lastAction?: string | null;
  gameId?: string | null;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  isConnected,
  error,
  connectionAttempts = 0,
  onReconnect,
  lastAction = null,
  gameId = null,
}) => {
  if (isConnected) {
    return (
      <div className="flex items-center gap-2 text-green-400 text-sm">
        <Wifi className="w-4 h-4" />
        <span>Conectado</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 text-red-400 text-sm">
        <AlertCircle className="w-4 h-4" />
        <div>
          <div>{error}</div>
          {lastAction && (
            <div className="text-xs text-red-200">Acción: {lastAction}</div>
          )}
          {gameId && (
            <div className="text-xs text-gray-300 font-mono">
              Game: {gameId}
            </div>
          )}
        </div>
        {onReconnect && (
          <button
            onClick={onReconnect}
            className="ml-2 px-2 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700"
          >
            Reintentar
          </button>
        )}
      </div>
    );
  }

  if (connectionAttempts > 0) {
    return (
      <div className="flex items-center gap-2 text-yellow-400 text-sm">
        <RotateCcw className="w-4 h-4 animate-spin" />
        <div>
          <div>Reconectando... (intento {connectionAttempts})</div>
          {lastAction && (
            <div className="text-xs text-yellow-200">
              Acción pendiente: {lastAction}
            </div>
          )}
          {gameId && (
            <div className="text-xs text-gray-300 font-mono">
              Game: {gameId}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-gray-400 text-sm">
      <WifiOff className="w-4 h-4" />
      <div>
        <div>Desconectado</div>
        {lastAction && (
          <div className="text-xs text-gray-500">
            Acción pendiente: {lastAction}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConnectionStatus;
