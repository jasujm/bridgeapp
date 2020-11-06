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

export interface Deal {
    calls: Array<PositionCallPair>;
}
