import React from 'react';
import { Card as CardType, Zone, Faction } from '../types/game';
import { Sword, Shield, Star, Zap } from 'lucide-react';

interface CardProps {
    card: CardType;
    onClick?: () => void;
    isPlayable?: boolean;
    isSelected?: boolean;
}

const factionColors = {
    [Faction.POLICE]: 'faction-police',
    [Faction.MAFIA]: 'faction-mafia',
    [Faction.DETECTIVE]: 'faction-detective',
    [Faction.THIEF]: 'faction-thief',
    [Faction.WILDCARD]: 'faction-wildcard'
};

const zoneIcons = {
    [Zone.BRUTES]: Sword,
    [Zone.SHOOTERS]: Zap,
    [Zone.TALKERS]: Star
};

const Card: React.FC<CardProps> = ({ card, onClick, isPlayable, isSelected }) => {
    const ZoneIcon = card.zone ? zoneIcons[card.zone] : null;

    return (
        <div
            className={`
        relative w-32 h-44 rounded-lg border-2 p-2 cursor-pointer
        card-shadow card-hover select-none
        ${factionColors[card.faction]}
        ${isSelected ? 'ring-4 ring-yellow-400' : ''}
        ${isPlayable ? 'hover:ring-2 hover:ring-white' : ''}
        ${!isPlayable && onClick ? 'opacity-60' : ''}
      `}
            onClick={isPlayable ? onClick : undefined}
        >
            {/* Card Header */}
            <div className="flex justify-between items-start mb-1">
                <div className="flex items-center gap-1">
                    {ZoneIcon && <ZoneIcon className="w-3 h-3" />}
                    {card.card_type === 'leader' && <Star className="w-3 h-3 text-yellow-400" />}
                </div>
                <div className="text-xs font-bold bg-black/30 px-1 rounded">
                    {card.cost}
                </div>
            </div>

            {/* Card Name */}
            <h3 className="text-xs font-bold text-white mb-1 leading-tight">
                {card.name}
            </h3>

            {/* Stats */}
            {(card.attack > 0 || card.defense > 0) && (
                <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-1 text-red-400">
                        <Sword className="w-3 h-3" />
                        <span className="text-xs font-bold">{card.attack}</span>
                    </div>
                    <div className="flex items-center gap-1 text-blue-400">
                        <Shield className="w-3 h-3" />
                        <span className="text-xs font-bold">{card.defense}</span>
                    </div>
                </div>
            )}

            {/* Description */}
            <p className="text-xs text-gray-300 leading-tight overflow-hidden">
                {card.description}
            </p>

            {/* Faction Badge */}
            <div className="absolute bottom-1 right-1">
                <div className="text-xs px-1 py-0.5 bg-black/50 rounded capitalize text-white">
                    {card.faction}
                </div>
            </div>
        </div>
    );
};

export default Card;