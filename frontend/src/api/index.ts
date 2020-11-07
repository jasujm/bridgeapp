// FIXME: Handle HTTP errors
// FIXME: Validate responses and handle errors

import axios, { AxiosRequestConfig } from "axios"
import { Deal, Call, Card, Self, EventCallback } from "./types"

function defaultWsBaseUrl() {
    const protocol = window.location.protocol.includes("https") ? "wss:" : "ws:";
    return `${protocol}//${window.location.hostname}`;
}

const wsBaseUrl = `${process.env.VUE_APP_BRIDGEAPP_WEBSOCKET_PREFIX || defaultWsBaseUrl()}/api/v1`;

const client = axios.create({
    baseURL: `${process.env.VUE_APP_BRIDGEAPP_API_PREFIX || ""}/api/v1/`
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

    async joinGame(gameUuid: string) {
        await this.request({
            method: "post",
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
        return response.data.deal as Deal;
    }

    async getSelf(gameUuid: string) {
        const response = await this.request({
            method: "get",
            url: `/games/${gameUuid}/self`,
        });
        return response.data as Self;
    }

    subscribe(gameUuid: string, callback: EventCallback) {
        const ws = new WebSocket(`${wsBaseUrl}/games/${gameUuid}/ws`);
        ws.onmessage = async function(message) {
            const text = await message.data.text();
            callback(JSON.parse(text));
        };
        return ws;
    }
}
