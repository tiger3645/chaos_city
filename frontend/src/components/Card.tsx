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
    [Zone.FIGHTER]: Sword,
    [Zone.GUNSINGER]: Zap,
    [Zone.TALKER]: Star,
};

const Card: React.FC<CardProps> = ({ card, onClick, isPlayable, isSelected }) => {
    const ZoneIcon = card.zone ? zoneIcons[card.zone] : Star;

    return (
        <div
            className={`relative w-48 h-96 rounded-lg border-2 p-2 cursor-pointer
        card-shadow card-hover select-none
        ${factionColors[card.faction]}
        ${isSelected ? 'ring-4 ring-yellow-400' : ''}
        ${isPlayable ? 'hover:ring-2 hover:ring-white' : ''}
        ${!isPlayable && onClick ? 'opacity-60' : ''}`}
            onClick={isPlayable ? onClick : undefined}
        >
            {/* Card Header */}
            <div className="flex justify-between items-start mb-1">
                <div className="flex items-center gap-1 border border-gray-600 bg-black/30 px-1 rounded">
                    {ZoneIcon ? <ZoneIcon className="w-3 h-6" /> : null}
                </div>
                <div className="text-lg font-bold bg-black/30 px-1 rounded">
                    {card.value}
                </div>
            </div>

            {/* Card Name */}
            <h3 className="text-xl font-bold text-white mb-2 leading-tight h-12 overflow-hidden">
                {card.name}
            </h3>
            <hr className="border-gray-600 mb-2" />

            {/* Stats */}
            {(card.attack > 0 || card.defense > 0) && (
                <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-1 text-red-400 border border-red-600 p-1 rounded bg-black/20">
                        <Sword className="w-4 h-4" />
                        <span className="text-md font-bold">{card.attack}</span>
                    </div>
                    <div className="flex items-center gap-1 text-blue-400 border border-blue-600 p-1 rounded bg-black/20">
                        <Shield className="w-4 h-4" />
                        <span className="text-md font-bold">{card.defense}</span>
                    </div>
                </div>
            )}

            {/* Description */}
            <p className="text-md text-gray-100 leading-tight overflow-hidden">
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