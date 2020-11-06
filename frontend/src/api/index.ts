// FIXME: Handle HTTP errors
// FIXME: Validate responses and handle errors

import axios, { AxiosRequestConfig } from "axios"
import { Deal, Call, Card, Self } from "./types"

const client = axios.create({
    baseURL: `${process.env.VUE_APP_BRIDGEAPP_API_PREFIX || ""}/api/v1/`
});

export default class {
    private username: string | null = null;

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
}
