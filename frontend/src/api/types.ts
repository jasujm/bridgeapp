export enum Position {
    north = "north",
    east = "east",
    south = "south",
    west = "west",
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
    _1 = "1",
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
    suit: string;
}

export class Cards {
    north: Array<Card | null> = [];
    east: Array<Card | null> = [];
    south: Array<Card | null> = [];
    west: Array<Card | null> = [];
}

export class Deal {
    calls: Array<PositionCallPair> = [];
    cards: Record<Position, Array<Card | null>> = new Cards();
}

export class Self {
    position: Position = Position.south;
    allowedCalls: Array<Call> = [];
}
