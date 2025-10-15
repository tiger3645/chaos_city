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
    FIGHTER = 'fighter',
    GUNSINGER = 'gunslinger',
    TALKER = 'talker'
}

export type Phase = 'draw' | 'deploy' | 'action' | 'resolution';

export interface Card {
    id: number;
    game_id: string;
    name: string;
    faction: Faction;
    type: CardType;
    zone?: Zone;
    attack: number;
    defense: number;
    value: number;
    description: string;
    ability?: string;
}

export interface Player {
    id: string;
    name: string;
    reputation: number;
    hand_cards: Array<Card>;
    deck_count: number;
    field: Record<Zone, Card[]>;
    coins: number;
}

export interface GameState {
    game_id: string;
    current_player: number;
    turn: number;
    phase: Phase;
    winner?: string;
    players: Player[];
    active_environment_card: Card | null;
    available_coins: number;
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