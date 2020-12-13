// FIXME: Validate responses and handle errors

import axios, { AxiosRequestConfig, AxiosError } from "axios"
import ReconnectingWebSocket from "reconnecting-websocket"
import {
    Deal,
    Call,
    Card,
    Self,
    Event,
    EventHandlers,
    ErrorSeverity,
    ErrorMessage,
    DealResult,
    Position,
    PlayersInGame,
} from "./types"

function defaultWsBaseUrl() {
    const protocol = window.location.protocol.includes("https") ? "wss:" : "ws:";
    return `${protocol}//${window.location.hostname}`;
}

const wsBaseUrl = `${process.env.VUE_APP_BRIDGEAPP_WEBSOCKET_PREFIX || defaultWsBaseUrl()}/api/v1`;

const client = axios.create({
    baseURL: `${process.env.VUE_APP_BRIDGEAPP_API_PREFIX || ""}/api/v1/`,
    timeout: 3000,
});

export default class {
    private username?: string;

    private request(config: AxiosRequestConfig) {
        if (this.username) {
            config.auth = {
                username: this.username,
                password: "",
            };
        }
        return client(config);
    }

    authenticate(username: string) {
        this.username = username;
    }

    async createGame() {
        const response = await this.request({
            method: "post",
            url: "/games",
        });
        return response.data as string;
    }

    async joinGame(gameUuid: string, position?: Position) {
        await this.request({
            method: "post",
            url: `/games/${gameUuid}/players`,
            params: { position },
        });
    }

    async leaveGame(gameUuid: string) {
        await this.request({
            method: "delete",
            url: `/games/${gameUuid}/players`,
        });
    }

    async makeCall(gameUuid: string, call: Call) {
        await this.request({
            method: "post",
            url: `/games/${gameUuid}/calls`,
            data: call,
        });
    }

    async playCard(gameUuid: string, card: Card) {
        await this.request({
            method: "post",
            url: `/games/${gameUuid}/trick`,
            data: card,
        });
    }

    async getDeal(gameUuid: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameUuid}`,
        });
        return {
            deal: response.data.deal as Deal | null,
            counter: Number(response.headers["x-counter"]) || null,
        };
    }

    async getSelf(gameUuid: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameUuid}/self`,
        });
        return response.data as Self;
    }

    async getResults(gameUuid: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameUuid}/results`,
        });
        return response.data as Array<DealResult>;
    }

    async getPlayers(gameUuid: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameUuid}/players`,
        });
        return response.data as PlayersInGame;
    }

    subscribe(gameUuid: string, handlers: EventHandlers) {
        const ws = new ReconnectingWebSocket(`${wsBaseUrl}/games/${gameUuid}/ws`);
        ws.onopen = function(event) {
            if (handlers.open) {
                handlers.open(event);
            }
        };
        ws.onmessage = async function(message) {
            const text = await message.data.text();
            const event = JSON.parse(text) as Event;
            // FIXME: Validating, type-safe approach is needed here
            // @ts-ignore
            const handler = handlers[event.type];
            if (handler) {
                handler(event);
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
