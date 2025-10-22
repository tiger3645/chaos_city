import React, { useState } from "react";
import { Card as CardType, Zone, Faction } from "../types/game";
import { Sword, Shield, Star, Zap } from "lucide-react";
import { CardStats } from "../types/effects";
import CardStatsTooltip from "./CardStatsTooltip";

interface CardProps {
  card: CardType;
  onClick?: () => void;
  isPlayable?: boolean;
  isSelected?: boolean;
  effectiveStats?: CardStats;
  onHover?: () => void;
  onHoverEnd?: () => void;
}

const factionColors = {
  [Faction.POLICE]: "faction-police",
  [Faction.MAFIA]: "faction-mafia",
  [Faction.DETECTIVE]: "faction-detective",
  [Faction.THIEF]: "faction-thief",
  [Faction.WILDCARD]: "faction-wildcard",
};

const zoneIcons = {
  [Zone.FIGHTER]: Sword,
  [Zone.GUNSINGER]: Zap,
  [Zone.TALKER]: Star,
};

const Card: React.FC<CardProps> = ({
  card,
  onClick,
  isPlayable,
  isSelected,
  effectiveStats,
  onHover,
  onHoverEnd,
}) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  const ZoneIcon = card.zone ? zoneIcons[card.zone] : Star;

  // Use effective stats if provided, otherwise use base stats
  const displayAttack = effectiveStats?.attack ?? card.attack;
  const displayDefense = effectiveStats?.defense ?? card.defense;
  const hasModifiers =
    effectiveStats &&
    (effectiveStats.attack !== effectiveStats.base_attack ||
      effectiveStats.defense !== effectiveStats.base_defense);

  const handleMouseEnter = (e: React.MouseEvent) => {
    setTooltipPosition({ x: e.clientX, y: e.clientY });
    setShowTooltip(true);
    onHover?.();
  };

  const handleMouseLeave = () => {
    setShowTooltip(false);
    onHoverEnd?.();
  };

  return (
    <>
      <div
        className={`card relative rounded-lg border-2 cursor-pointer
            card-shadow card-hover select-none
            flex flex-col justify-between
            ${factionColors[card.faction]}
            ${isSelected ? "ring-4 ring-yellow-400" : ""}
            ${isPlayable ? "hover:ring-2 hover:ring-white" : ""}
            ${!isPlayable && onClick ? "opacity-60" : ""}`}
        onClick={isPlayable ? onClick : undefined}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {/* Card Header */}
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-1 border border-gray-600 bg-black/30 px-1 rounded-lg">
            {ZoneIcon ? <ZoneIcon className="w-4 h-7" /> : null}
          </div>
          <div className="flex items-center justify-center text-lg font-bold px-1 w-6 h-8 rounded-lg">
            {card.value}
          </div>
        </div>

        {/* Card Name */}
        {/* <h3 className="text-xl font-bold text-white mb-2 leading-tight h-12 overflow-hidden">
          {card.name}
        </h3>
        <hr className="border-gray-600 mb-2" /> */}

        {/* Stats */}
        {(card.attack > 0 || card.defense > 0) && (
          <div className="flex justify-between items-center">
            <div
              className={`flex items-center border p-[3px] rounded-lg bg-black/20 ${
                hasModifiers && displayAttack !== card.attack
                  ? displayAttack > card.attack
                    ? "text-green-400 border-green-600"
                    : "text-red-400 border-red-600"
                  : "text-red-400 border-red-600"
              }`}
            >
              <Sword className="w-4 h-4" />
              <span className="text-md font-bold">{displayAttack}</span>
            </div>
            <div
              className={`flex items-center border p-[3px] rounded-lg bg-black/20 ${
                hasModifiers && displayDefense !== card.defense
                  ? displayDefense > card.defense
                    ? "text-green-400 border-green-600"
                    : "text-red-400 border-red-600"
                  : "text-blue-400 border-blue-600"
              }`}
            >
              <Shield className="w-4 h-4" />
              <span className="text-md font-bold">{displayDefense}</span>
            </div>
          </div>
        )}

        {/* Description */}
        {/* <p className="text-md text-gray-100 leading-tight overflow-hidden">
          {card.description}
        </p> */}

        {/* Faction Badge */}
        {/* <div className="absolute bottom-1 right-1">
          <div className="text-xs px-1 py-0.5 bg-black/50 rounded capitalize text-white">
            {card.faction}
          </div>
        </div> */}
      </div>

      {/* Tooltip for effective stats */}
      {effectiveStats && showTooltip && (
        <CardStatsTooltip
          stats={effectiveStats}
          position={tooltipPosition}
          visible={showTooltip}
        />
      )}
    </>
  );
};

export default Card;
