import React, { useState } from 'react';
import { Faction } from '../types/game';
import { Gamepad2, Users, Sword, Eye, Zap, Star } from 'lucide-react';

interface GameSetupProps {
    onCreateGame: (playerName: string, playerFaction: Faction) => void;
    onJoinGame: (gameId: string, playerName: string, playerFaction: Faction) => void;
    isConnected: boolean;
}

const factionInfo = {
    [Faction.POLICE]: {
        name: 'Policías',
        color: 'text-blue-400',
        icon: Sword,
        description: 'Control y resistencia. Fuertes contra Ladrones, débiles contra Mafiosos.'
    },
    [Faction.MAFIA]: {
        name: 'Mafiosos',
        color: 'text-red-400',
        icon: Zap,
        description: 'Agresión y fuerza bruta. Fuertes contra Policías, débiles contra Detectives.'
    },
    [Faction.DETECTIVE]: {
        name: 'Detectives',
        color: 'text-green-400',
        icon: Eye,
        description: 'Astucia e investigación. Fuertes contra Mafiosos, débiles contra Ladrones.'
    },
    [Faction.THIEF]: {
        name: 'Ladrones',
        color: 'text-purple-400',
        icon: Users,
        description: 'Sigilo y evasión. Fuertes contra Detectives, débiles contra Policías.'
    },
    [Faction.WILDCARD]: {
        name: 'Wildcards',
        color: 'text-yellow-400',
        icon: Star,
        description: 'Caos y flexibilidad. Sin ventajas ni debilidades fijas.'
    }
};

const GameSetup: React.FC<GameSetupProps> = ({ onCreateGame, onJoinGame, isConnected }) => {
    const [mode, setMode] = useState<'create' | 'join'>('create');
    const [playerName, setPlayerName] = useState('Jugador 1');
    const [playerFaction, setPlayerFaction] = useState<Faction>(Faction.POLICE);
    const [gameId, setGameId] = useState('');
    const [joinPlayerName, setJoinPlayerName] = useState('Jugador 2');
    const [joinPlayerFaction, setJoinPlayerFaction] = useState<Faction>(Faction.MAFIA);

    const handleCreateGame = () => {
        if (playerName.trim()) {
            onCreateGame(playerName.trim(), playerFaction);
        }
    };

    const handleJoinGame = () => {
        if (gameId.trim() && joinPlayerName.trim()) {
            onJoinGame(gameId.trim(), joinPlayerName.trim(), joinPlayerFaction);
        }
    };

    if (!isConnected) {
        return (
            <div className="min-h-screen bg-chaos-dark flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin w-12 h-12 border-4 border-chaos-gold border-t-transparent rounded-full mx-auto mb-4"></div>
                    <h2 className="text-2xl font-bold text-white mb-2">Conectando al servidor...</h2>
                    <p className="text-gray-400">Esperando conexión WebSocket</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-chaos-dark p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-5xl font-display font-bold text-chaos-gold mb-4">
                        Ciudad del Caos
                    </h1>
                    <p className="text-xl text-gray-300">
                        Chicago, 1946. Lucha por el control de la ciudad.
                    </p>
                </div>

                {/* Mode Selection */}
                <div className="flex justify-center mb-8">
                    <div className="bg-black/30 p-1 rounded-lg">
                        <button
                            onClick={() => setMode('create')}
                            className={`px-6 py-2 rounded font-bold transition-colors ${mode === 'create'
                                ? 'bg-chaos-gold text-black'
                                : 'text-white hover:bg-white/10'
                                }`}
                        >
                            Crear Juego
                        </button>
                        <button
                            onClick={() => setMode('join')}
                            className={`px-6 py-2 rounded font-bold transition-colors ${mode === 'join'
                                ? 'bg-chaos-gold text-black'
                                : 'text-white hover:bg-white/10'
                                }`}
                        >
                            Unirse a Juego
                        </button>
                    </div>
                </div>

                {mode === 'create' ? (
                    <div className="bg-black/30 p-8 rounded-lg">
                        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                            <Gamepad2 className="w-6 h-6" />
                            Crear Nuevo Juego
                        </h2>

                        {/* Player Setup */}
                        <div className="mb-6">
                            <h3 className="text-lg font-bold text-white mb-4">Tu Jugador</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-white mb-2">Nombre:</label>
                                    <input
                                        type="text"
                                        value={playerName}
                                        onChange={(e) => setPlayerName(e.target.value)}
                                        className="w-full p-2 rounded bg-gray-800 text-white border border-gray-600"
                                        placeholder="Ingresa tu nombre"
                                    />
                                </div>
                                <div>
                                    <label className="block text-white mb-2">Facción:</label>
                                    <select
                                        value={playerFaction}
                                        onChange={(e) => setPlayerFaction(e.target.value as Faction)}
                                        className="w-full p-2 rounded bg-gray-800 text-white border border-gray-600"
                                    >
                                        {Object.entries(factionInfo).map(([faction, info]) => (
                                            <option key={faction} value={faction}>
                                                {info.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="mb-4 p-4 bg-blue-900/30 rounded border-l-4 border-blue-400">
                            <p className="text-blue-200 text-sm">
                                <strong>Nota:</strong> Después de crear el juego, comparte el ID con otro jugador para que se una a la partida.
                            </p>
                        </div>

                        <button
                            onClick={handleCreateGame}
                            disabled={!playerName.trim()}
                            className="w-full py-3 bg-chaos-gold text-black font-bold rounded hover:bg-opacity-80 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Crear Juego
                        </button>
                    </div>
                ) : (
                    <div className="bg-black/30 p-8 rounded-lg">
                        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                            <Users className="w-6 h-6" />
                            Unirse a Juego Existente
                        </h2>

                        <div className="mb-6">
                            <label className="block text-white mb-2">ID del Juego:</label>
                            <input
                                type="text"
                                value={gameId}
                                onChange={(e) => setGameId(e.target.value)}
                                placeholder="Ingresa el ID del juego..."
                                className="w-full p-3 rounded bg-gray-800 text-white border border-gray-600"
                            />
                        </div>

                        {/* Join Player Setup */}
                        <div className="mb-6">
                            <h3 className="text-lg font-bold text-white mb-4">Tu Jugador</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-white mb-2">Nombre:</label>
                                    <input
                                        type="text"
                                        value={joinPlayerName}
                                        onChange={(e) => setJoinPlayerName(e.target.value)}
                                        className="w-full p-2 rounded bg-gray-800 text-white border border-gray-600"
                                        placeholder="Ingresa tu nombre"
                                    />
                                </div>
                                <div>
                                    <label className="block text-white mb-2">Facción:</label>
                                    <select
                                        value={joinPlayerFaction}
                                        onChange={(e) => setJoinPlayerFaction(e.target.value as Faction)}
                                        className="w-full p-2 rounded bg-gray-800 text-white border border-gray-600"
                                    >
                                        {Object.entries(factionInfo).map(([faction, info]) => (
                                            <option key={faction} value={faction}>
                                                {info.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={handleJoinGame}
                            disabled={!gameId.trim() || !joinPlayerName.trim()}
                            className="w-full py-3 bg-chaos-blue text-white font-bold rounded hover:bg-opacity-80 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Unirse al Juego
                        </button>
                    </div>
                )}

                {/* Faction Information */}
                <div className="mt-8 bg-black/30 p-8 rounded-lg">
                    <h2 className="text-2xl font-bold text-white mb-6">Facciones</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(factionInfo).map(([faction, info]) => {
                            const Icon = info.icon;
                            return (
                                <div key={faction} className="bg-black/30 p-4 rounded border-l-4 border-gray-600">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Icon className={`w-5 h-5 ${info.color}`} />
                                        <h3 className={`font-bold ${info.color}`}>{info.name}</h3>
                                    </div>
                                    <p className="text-sm text-gray-300">{info.description}</p>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GameSetup;