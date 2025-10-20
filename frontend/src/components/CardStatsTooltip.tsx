import React from 'react';
import { Sword, Shield, TrendingUp, TrendingDown } from 'lucide-react';
import { CardStats } from '../types/effects';

interface CardStatsTooltipProps {
    stats: CardStats;
    position?: { x: number; y: number };
    visible: boolean;
}

const CardStatsTooltip: React.FC<CardStatsTooltipProps> = ({
    stats,
    position,
    visible
}) => {
    if (!visible) return null;

    const hasModifiers = stats.modifiers && stats.modifiers.length > 0;
    const attackModified = stats.attack !== stats.base_attack;
    const defenseModified = stats.defense !== stats.base_defense;

    return (
        <div
            className="fixed bg-gray-900 border-2 border-purple-500 rounded-lg p-3 shadow-2xl z-50 
                       pointer-events-none animate-fade-in min-w-64"
            style={{
                left: position ? `${position.x + 10}px` : '50%',
                top: position ? `${position.y + 10}px` : '50%'
            }}
        >
            {/* Title */}
            <h3 className="text-lg font-bold text-white mb-2 border-b border-gray-700 pb-1">
                Effective Stats
            </h3>

            {/* Stats Display */}
            <div className="space-y-2 mb-2">
                {/* Attack */}
                <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-2">
                        <Sword className="w-4 h-4 text-red-400" />
                        <span className="text-white font-semibold">Attack:</span>
                    </div>
                    <div className="flex items-center gap-2">
                        {attackModified && (
                            <>
                                <span className="text-gray-500 line-through text-sm">
                                    {stats.base_attack}
                                </span>
                                {stats.attack > stats.base_attack ? (
                                    <TrendingUp className="w-4 h-4 text-green-400" />
                                ) : (
                                    <TrendingDown className="w-4 h-4 text-red-400" />
                                )}
                            </>
                        )}
                        <span className={`font-bold text-lg ${attackModified
                                ? stats.attack > stats.base_attack
                                    ? 'text-green-400'
                                    : 'text-red-400'
                                : 'text-white'
                            }`}>
                            {stats.attack}
                        </span>
                    </div>
                </div>

                {/* Defense */}
                <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-2">
                        <Shield className="w-4 h-4 text-blue-400" />
                        <span className="text-white font-semibold">Defense:</span>
                    </div>
                    <div className="flex items-center gap-2">
                        {defenseModified && (
                            <>
                                <span className="text-gray-500 line-through text-sm">
                                    {stats.base_defense}
                                </span>
                                {stats.defense > stats.base_defense ? (
                                    <TrendingUp className="w-4 h-4 text-green-400" />
                                ) : (
                                    <TrendingDown className="w-4 h-4 text-red-400" />
                                )}
                            </>
                        )}
                        <span className={`font-bold text-lg ${defenseModified
                                ? stats.defense > stats.base_defense
                                    ? 'text-green-400'
                                    : 'text-red-400'
                                : 'text-white'
                            }`}>
                            {stats.defense}
                        </span>
                    </div>
                </div>
            </div>

            {/* Modifiers List */}
            {hasModifiers && (
                <div className="border-t border-gray-700 pt-2 mt-2">
                    <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">
                        Active Modifiers:
                    </h4>
                    <div className="space-y-1">
                        {stats.modifiers!.map((modifier, index) => (
                            <div key={index} className="text-xs text-gray-300 flex items-start gap-2">
                                <span className="text-purple-400">•</span>
                                <div className="flex-1">
                                    <span className="font-semibold">{modifier.source}:</span>
                                    {modifier.attack !== 0 && (
                                        <span className={modifier.attack > 0 ? 'text-green-400' : 'text-red-400'}>
                                            {' '}{modifier.attack > 0 ? '+' : ''}{modifier.attack} ATK
                                        </span>
                                    )}
                                    {modifier.attack !== 0 && modifier.defense !== 0 && ', '}
                                    {modifier.defense !== 0 && (
                                        <span className={modifier.defense > 0 ? 'text-green-400' : 'text-red-400'}>
                                            {modifier.defense > 0 ? '+' : ''}{modifier.defense} DEF
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* No Modifiers */}
            {!hasModifiers && (
                <div className="border-t border-gray-700 pt-2 mt-2">
                    <p className="text-xs text-gray-500 italic">
                        No active modifiers
                    </p>
                </div>
            )}
        </div>
    );
};

export default CardStatsTooltip;
