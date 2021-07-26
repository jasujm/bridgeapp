import { Event as WsEvent } from "reconnecting-websocket";

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
  id = "";
  self = "";
  positionInTurn?: Position;
  calls: Array<PositionCallPair> = [];
  declarer: Position | null = null;
  contract: Contract | null = null;
  cards: Record<Position, Array<Card | null>> = new Cards();
  tricks: Array<Trick> = [];
  vulnerability: Vulnerability = { northSouth: false, eastWest: false };
}

export class PlayerState {
  position: Position | null = null;
  allowedCalls: Array<Call> = [];
  allowedCards: Array<Card> = [];
}

export interface DuplicateResult {
  partnership: Partnership | null;
  score: number;
}

export interface DealResult {
  deal: string;
  result: DuplicateResult | null;
}

export interface Player {
  id: string;
  username: string;
}

export class PlayersInGame {
  north: Player | null = null;
  east: Player | null = null;
  south: Player | null = null;
  west: Player | null = null;
}

export class GameSummary {
  id = "";
  self = "";
  name = "";
}

export class GameCreate {
  name = "";
  isPublic = true;
}

export class Game {
  id = "";
  self = "";
  name = "";
  deal: Deal | null = null;
  me = new PlayerState();
  results: Array<DealResult> = [];
  players = new PlayersInGame();
}

export interface Game {
  game: Game;
  counter: number | null;
}

export interface GameCounterPair {
  game: Game;
  counter: number | null;
}

export interface Event {
  type: string;
  game: string;
  counter: number;
}

export interface PlayerEvent extends Event {
  type: "player";
  position: Position;
  player: string | null;
}

export interface DealEvent extends Event {
  type: "deal";
}

export interface TurnEvent extends Event {
  type: "turn";
  position: Position;
}

export interface CallEvent extends Event {
  type: "call";
  position: Position;
  call: Call;
  index: number;
}

export interface BiddingEvent extends Event {
  type: "bidding";
  declarer: Position | null;
  contract: Contract | null;
}

export interface PlayEvent extends Event {
  type: "play";
  position: Position;
  card: Card;
  trick: number;
  index: number;
}

export interface DummyEvent extends Event {
  type: "dummy";
  position: Position;
  cards: Array<Card>;
}

export interface TrickEvent extends Event {
  type: "trick";
  winner: Position;
  index: number;
}

export interface DealEndEvent extends Event {
  type: "dealend";
  deal: string;
  contract: Contract | null;
  tricksWon: number | null;
  result: DuplicateResult;
}

export type AnyEvent =
  | PlayerEvent
  | DealEvent
  | TurnEvent
  | CallEvent
  | BiddingEvent
  | PlayEvent
  | DummyEvent
  | TrickEvent
  | DealEndEvent;

export interface EventHandlers {
  open?: (event: WsEvent) => void;
  player?: (event: PlayerEvent) => void;
  deal?: (event: DealEvent) => void;
  turn?: (event: TurnEvent) => void;
  call?: (event: CallEvent) => void;
  bidding?: (event: BiddingEvent) => void;
  play?: (event: PlayEvent) => void;
  dummy?: (event: DummyEvent) => void;
  trick?: (event: TrickEvent) => void;
  dealend?: (event: DealEndEvent) => void;
}

export enum ErrorSeverity {
  danger = "danger",
  warning = "warning",
}

export class ErrorMessage {
  constructor(
    readonly message = "",
    readonly severity: ErrorSeverity = ErrorSeverity.danger
  ) {}
}

export interface ValidationError {
  loc: Array<string>;
  msg: string;
}
