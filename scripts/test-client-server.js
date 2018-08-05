const uuid = require("uuid/v4");
const client = require("../bridge/client");
const { spawn } = require("child_process");

const secretKey = "JTKVSB%%)wK0E.X)V>+}o?pNmC{O&4W4b!Ni{Lh6";
const publicKey = "rq:rM>}U?@Lns47E1%kR.o@n%FcmmsL/@{H8]yf7";

const server = spawn("bridge", ["--config", "-", "tcp://127.0.0.1:5555"]);
server.stdin.write(`curve_secret_key = "${secretKey}"\n`);
server.stdin.end(`curve_public_key = "${publicKey}"\n`);

const n_clients = parseInt(process.argv[2]) || 1;
for (let n = 0; n < n_clients; ++n) {
    const gameUuid = uuid();
    for (let i = 0; i < 4; ++i) {
        setTimeout(
            () => client("tcp://127.0.0.1:5555", publicKey, gameUuid, i == 0)
                .catch((err) => console.log("failed with error:", err)),
            i * 100);
    }
}
