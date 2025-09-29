export enum Faction {
    POLICE = 'police',
    MAFIA = 'mafia',
    DETECTIVE = 'detective',
    THIEF = 'thief',
    WILDCARD = 'wildcard'
}

export enum CardType {
    LEADER = 'leader',
    CHARACTER = 'character',
    EFFECT = 'effect',
    ENVIRONMENT = 'environment'
}

export enum Zone {
    BRUTES = 'brutes',
    SHOOTERS = 'shooters',
    TALKERS = 'talkers'
}

export type Phase = 'draw' | 'deploy' | 'action' | 'resolution';

export interface Card {
    id: string;
    name: string;
    faction: Faction;
    card_type: CardType;
    zone?: Zone;
    attack: number;
    defense: number;
    cost: number;
    description: string;
    ability?: string;
    is_unique: boolean;
}

export interface Player {
    id: string;
    name: string;
    reputation: number;
    hand_count: number;
    deck_count: number;
    field: Record<Zone, Card[]>;
    leader?: Card;
}

export interface GameState {
    game_id: string;
    current_player: number;
    turn: number;
    phase: Phase;
    winner?: string;
    players: Player[];
    active_environments: Record<Zone, Card | null>;
}

export interface WebSocketMessage {
    type: string;
    [key: string]: any;
}

export interface AttackResult {
    success: boolean;
    message: string;
    destroyed?: string;
    damage?: number;
    reputation_damage?: number;
    game_over?: boolean;
    winner?: string;
}