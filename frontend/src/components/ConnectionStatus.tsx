import React from 'react';
import { Wifi, WifiOff, RotateCcw, AlertCircle } from 'lucide-react';

interface ConnectionStatusProps {
    isConnected: boolean;
    error: string | null;
    connectionAttempts?: number;
    onReconnect?: () => void;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
    isConnected,
    error,
    connectionAttempts = 0,
    onReconnect
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
                <span>{error}</span>
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
                <span>Reconectando... (intento {connectionAttempts})</span>
            </div>
        );
    }

    return (
        <div className="flex items-center gap-2 text-gray-400 text-sm">
            <WifiOff className="w-4 h-4" />
            <span>Desconectado</span>
        </div>
    );
};

export default ConnectionStatus;