export enum Position {
    north = "north",
    east = "east",
    south = "south",
    west = "west",
}

export enum Partnership {
    northSouth = "northSouth",
    eastWest = "eastWest",
}

export enum Strain {
    clubs = "clubs",
    diamonds = "diamonds",
    hearts = "hearts",
    spades = "spades",
    notrump = "notrump",
}

export enum CallType {
    bid = "bid",
    pass = "pass",
    double = "double",
    redouble = "redouble",
}

export interface Bid {
    level: number;
    strain: Strain;
}

export interface Call {
    type: CallType;
    bid?: Bid;
}

export interface PositionCallPair {
    position: Position;
    call: Call;
}

export enum Rank {
    _2 = "2",
    _3 = "3",
    _4 = "4",
    _5 = "5",
    _6 = "6",
    _7 = "7",
    _8 = "8",
    _9 = "9",
    _10 = "10",
    jack = "jack",
    queen = "queen",
    king = "king",
    ace = "ace",
}

export enum Suit {
    clubs = "clubs",
    diamonds = "diamonds",
    hearts = "hearts",
    spades = "spades",
}

export interface Card {
    rank: Rank;
    suit: Suit;
}

export class Cards {
    north: Array<Card | null> = [];
    east: Array<Card | null> = [];
    south: Array<Card | null> = [];
    west: Array<Card | null> = [];
}

export interface PositionCardPair {
    position: Position;
    card: Card;
}

export interface Trick {
    cards?: Array<PositionCardPair>;
}

export interface Vulnerability {
    northSouth: boolean;
    eastWest: boolean;
}

export class Deal {
    positionInTurn?: Position;
    calls: Array<PositionCallPair> = [];
    cards: Record<Position, Array<Card | null>> = new Cards();
    tricks: Array<Trick> = [];
    vulnerability: Vulnerability = { northSouth: false, eastWest: false };
}

export class Self {
    position: Position = Position.south;
    allowedCalls: Array<Call> = [];
    allowedCards: Array<Card> = [];
}

export interface Event {
    game: string;
    type: string;
}

export interface Score {
    partnership: Partnership;
    score: number;
}

export interface DealEndEvent extends Event {
    score: Score | null;
}

export type EventCallback = (event: Event) => void;
