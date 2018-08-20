const uuid = require("uuid/v4");
const client = require("../bridge/client");
const { spawn } = require("child_process");

const secretKey = "JTKVSB%%)wK0E.X)V>+}o?pNmC{O&4W4b!Ni{Lh6";
const publicKey = "rq:rM>}U?@Lns47E1%kR.o@n%FcmmsL/@{H8]yf7";
const gameUuid = uuid();

function spawnBridge(positions, peers, cscntl, cspeer, port) {
    const server = spawn("bridge", ['--config', '-']);
    config = `bind_base_port = ${port}
curve_secret_key = "${secretKey}"
curve_public_key = "${publicKey}"
game {
  uuid = "${gameUuid}",
  positions_controlled = { ${positions.map((position) => `"${position}"`).join()} },
  peers = {
    ${peers.map((peer) => `{endpoint = "${peer}", server_key = "${publicKey}"}`).join()}
  },
  card_server = {
    control_endpoint = "${cscntl}",
    base_peer_endpoint = "${cspeer}",
  },
}
`;
    server.stdin.end(config);
}

function spawnCardServer(cntl, peer) {
    const server = spawn(
        "bridgecs",
        ['--secret-key-file', '-', '--public-key-file', '-', cntl, peer]);
    server.stdin.end(`${secretKey} ${publicKey}\n`);
}

spawnCardServer("tcp://127.0.0.1:5650", "tcp://127.0.0.1:5750");
spawnCardServer("tcp://127.0.0.1:5660", "tcp://127.0.0.1:5760");
spawnCardServer("tcp://127.0.0.1:5670", "tcp://127.0.0.1:5770");
spawnCardServer("tcp://127.0.0.1:5680", "tcp://127.0.0.1:5780");

spawnBridge(["north"], ["tcp://localhost:5560","tcp://localhost:5570","tcp://localhost:5580"], 'tcp://127.0.0.1:5650', 'tcp://127.0.0.1:5750', 5550);
spawnBridge(["east"], ["tcp://localhost:5550","tcp://localhost:5570","tcp://localhost:5580"], 'tcp://127.0.0.1:5660', 'tcp://127.0.0.1:5760', 5560);
spawnBridge(["south"], ["tcp://localhost:5550","tcp://localhost:5560","tcp://localhost:5580"], 'tcp://127.0.0.1:5670', 'tcp://127.0.0.1:5770', 5570);
spawnBridge(["west"], ["tcp://localhost:5550","tcp://localhost:5560","tcp://localhost:5570"], 'tcp://127.0.0.1:5680', 'tcp://127.0.0.1:5780', 5580);

client("tcp://127.0.0.1:5550", publicKey).catch((err) => console.log("failed with error:", err));
client("tcp://127.0.0.1:5560", publicKey).catch((err) => console.log("failed with error:", err));
client("tcp://127.0.0.1:5570", publicKey).catch((err) => console.log("failed with error:", err));
client("tcp://127.0.0.1:5580", publicKey).catch((err) => console.log("failed with error:", err));
