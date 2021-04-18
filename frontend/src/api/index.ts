import axios, { AxiosRequestConfig, AxiosError } from "axios"
import ReconnectingWebSocket from "reconnecting-websocket"
import {
    Player,
    Game,
    Deal,
    Call,
    Card,
    PlayerState,
    AnyEvent,
    EventHandlers,
    ErrorSeverity,
    ErrorMessage,
    DealResult,
    Position,
    PlayersInGame,
} from "./types"

export interface BasicAuth {
    username: string;
    password: string;
}

function defaultWsBaseUrl() {
    const protocol = window.location.protocol.includes("https") ? "wss:" : "ws:";
    return `${protocol}//${window.location.hostname}`;
}

const wsBaseUrl = `${process.env.VUE_APP_BRIDGEAPP_WEBSOCKET_PREFIX || defaultWsBaseUrl()}/api/v1`;

const client = axios.create({
    baseURL: `${process.env.VUE_APP_BRIDGEAPP_API_PREFIX || ""}/api/v1/`,
    timeout: 3000,
});

function callHandler<Event>(event: Event, handler?: (event: Event) => void) {
    if (handler) {
        handler(event);
    }
}

function getUrl(idOrUrl: string, base: string) {
    if (idOrUrl.match(/^https?:\/\//)) {
        return idOrUrl;
    }
    return base + idOrUrl;
}

export default class {
    private auth?: BasicAuth;

    private request(config: AxiosRequestConfig) {
        if (this.auth) {
            config.auth = this.auth;
        }
        return client(config);
    }

    async authenticate(auth: BasicAuth) {
        try {
            await client({
                method: "get",
                url: "/players/me",
                auth
            });
            this.auth = auth;
            return true;
        } catch (err) {
            return false;
        }
    }

    forgetAuth() {
        this.auth = undefined;
    }

    async createPlayer(username: string, password: string) {
        const response = await this.request({
            method: "post",
            url: "/players",
            data: { username, password },
        });
        return response.data as Player;
    }

    async changePassword(currentPassword: string, newPassword: string) {
        if (this.auth) {
            await client({
                method: "patch",
                url: "/players/me",
                auth: {
                    username: this.auth.username,
                    password: currentPassword,
                },
                data: {
                    password: newPassword,
                }
            });
            this.auth.password = newPassword;
        }
    }

    async getMe() {
        const response = await this.request({
            method: "get",
            url: "/players/me",
        });
        return response.data as Player;
    }

    async getPlayer(playerId: string) {
        const response = await this.request({
            method: "get",
            url: getUrl(playerId, "/players/"),
        });
        return response.data as Player;
    }

    async createGame() {
        const response = await this.request({
            method: "post",
            url: "/games",
        });
        return response.data as Game;
    }

    async joinGame(gameId: string, position?: Position) {
        await this.request({
            method: "post",
            url: `/games/${gameId}/players`,
            params: { position },
        });
    }

    async leaveGame(gameId: string) {
        await this.request({
            method: "delete",
            url: `/games/${gameId}/players`,
        });
    }

    async makeCall(gameId: string, call: Call) {
        await this.request({
            method: "post",
            url: `/games/${gameId}/calls`,
            data: call,
        });
    }

    async playCard(gameId: string, card: Card) {
        await this.request({
            method: "post",
            url: `/games/${gameId}/trick`,
            data: card,
        });
    }

    async getGame(gameId: string) {
        const response = await this.request({
            method: "get",
            url: getUrl(gameId, "/games/"),
        });
        return {
            game: response.data as Game | null,
            counter: Number(response.headers["x-counter"]) || null,
        };
    }

    async getDeal(gameId: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameId}/deal`,
        });
        return response.data as Deal | null;
    }

    async getPlayerState(gameId: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameId}/me`,
        });
        return response.data as PlayerState;
    }

    async getResults(gameId: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameId}/results`,
        });
        return response.data as Array<DealResult>;
    }

    async getPlayers(gameId: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameId}/players`,
        });
        return response.data as PlayersInGame;
    }

    subscribe(gameId: string, handlers: EventHandlers) {
        const ws = new ReconnectingWebSocket(`${wsBaseUrl}/games/${gameId}/ws`);
        ws.onopen = function(event) {
            if (handlers.open) {
                handlers.open(event);
            }
        };
        ws.onmessage = async function(message) {
            const text = await message.data.text();
            const event = JSON.parse(text) as AnyEvent;
            // This seems silly, but not sure if the type checker will allow it
            // any other way
            if (event.type == "player") {
                callHandler(event, handlers.player);
            } else if (event.type == "deal") {
                callHandler(event, handlers.deal);
            } else if (event.type == "turn") {
                callHandler(event, handlers.turn);
            } else if (event.type == "call") {
                callHandler(event, handlers.call);
            } else if (event.type == "bidding") {
                callHandler(event, handlers.bidding);
            } else if (event.type == "play") {
                callHandler(event, handlers.play);
            } else if (event.type == "dummy") {
                callHandler(event, handlers.dummy);
            } else if (event.type == "trick") {
                callHandler(event, handlers.trick);
            } else if (event.type == "dealend") {
                callHandler(event, handlers.dealend);
            }
        };
        return ws;
    }
}

export function getErrorMessage(err: Error) {
    const axiosError = err as AxiosError;
    if (axiosError.isAxiosError) {
        const response = axiosError.response;
        if (response) {
            const detail = response.data.detail;
            // 404 and 409 are due to user actions, and less severe
            // Other errors are bugs in the frontend or backend code
            const severity = [404, 409].includes(response.status) ?
                ErrorSeverity.warning : ErrorSeverity.danger;
            if (response.data.detail) {
                return new ErrorMessage(detail, severity);
            } else {
                return new ErrorMessage("Server error")
            }
        } else {
            // timeout
            return new ErrorMessage("Lost connection to the server");
        }
    }
    return null;
}
