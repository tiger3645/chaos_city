/**
 * Types for the card effects system
 */

export interface EffectChoice {
    id: string;
    name: string;
    description?: string;
    [key: string]: any;
}

export interface RevealedInfo {
    type: 'hand' | 'deck' | 'field' | 'other';
    cards?: Array<{
        id: string;
        name: string;
        [key: string]: any;
    }>;
    message?: string;
    [key: string]: any;
}

export interface CardPlayedMessage {
    type: 'card_played';
    player_id: string;
    card_game_id: string;
    zone: string | null;
    message: string;
    requires_choice: boolean;
    choices: EffectChoice[];
    revealed_info?: RevealedInfo;
    effect_id?: string;
}

export interface EffectContinuedMessage {
    type: 'effect_continued';
    message: string;
    requires_choice: boolean;
    choices: EffectChoice[];
    revealed_info?: RevealedInfo;
    effect_id?: string;
}

export interface CardStats {
    attack: number;
    defense: number;
    base_attack: number;
    base_defense: number;
    modifiers?: Array<{
        source: string;
        attack: number;
        defense: number;
    }>;
}

export interface CardStatsMessage {
    type: 'card_stats';
    card_game_id: string;
    stats: CardStats;
}

export interface AttackResultEnhanced {
    success: boolean;
    message: string;
    attacker_effective_attack?: number;
    attacker_effective_defense?: number;
    defender_effective_attack?: number;
    defender_effective_defense?: number;
    attacker_survived?: boolean;
    defender_survived?: boolean;
    triggered_effects?: string[];
}

export interface AttackResultMessage {
    type: 'attack_result';
    result: AttackResultEnhanced;
}

export interface EffectsTriggeredMessage {
    type: 'effects_triggered';
    effects: string[];
    message: string;
}

export interface CardPlayedBroadcastMessage {
    type: 'card_played_broadcast';
    player_id: string;
    card_game_id: string;
    zone: string | null;
}
