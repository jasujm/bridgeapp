import axios, { AxiosRequestConfig } from "axios"

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
        return response.data;
    }
}
