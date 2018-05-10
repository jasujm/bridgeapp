const uuid = require("uuid/v4");
const client = require('../bridge/client');
const { spawn } = require('child_process');

const server = spawn('bridge', ['tcp://127.0.0.1:5555']);

for (let n = 0; n < 10; ++n) {
    const gameUuid = uuid();
    for (let i = 0; i < 4; ++i) {
        setTimeout(
            () => client('tcp://127.0.0.1:5555', gameUuid, i == 0)
                .catch((err) => console.log('failed with error:', err)),
            i * 100);
    }
}
