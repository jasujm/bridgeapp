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

export enum Doubling {
    undoubled = "undoubled",
    doubled = "doubled",
    redoubled = "redoubled",
}

export interface Contract {
    bid: Bid;
    doubling: Doubling;
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
    cards: Array<PositionCardPair>;
    winner?: Position;
}

export interface Vulnerability {
    northSouth: boolean;
    eastWest: boolean;
}

export class Deal {
    positionInTurn?: Position;
    calls: Array<PositionCallPair> = [];
    declarer: Position | null = null;
    contract: Contract | null = null;
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
    counter: number;
}

export interface Score {
    partnership: Partnership;
    score: number;
}

export type DealEvent = Event;

export interface TurnEvent extends Event {
    position: Position;
}

export interface CallEvent extends Event {
    position: Position;
    call: Call;
}

export interface BiddingEvent extends Event {
    declarer: Position | null;
    contract: Contract | null;
}

export interface PlayEvent extends Event {
    position: Position;
    card: Card;
}

export interface DummyEvent extends Event {
    position: Position;
    cards: Array<Card>;
}

export interface TrickEvent extends Event {
    winner: Position;
}

export interface DealEndEvent extends Event {
    score: Score | null;
}

export interface EventHandlers {
    deal?: (event: DealEvent) => void;
    turn?: (event: TurnEvent) => void;
    call?: (event: CallEvent) => void;
    bidding?: (event: BiddingEvent) => void;
    play?: (event: PlayEvent) => void;
    dummy?: (event: DummyEvent) => void;
    trick?: (event: TrickEvent) => void;
    dealend?: (event: DealEndEvent) => void;
}
