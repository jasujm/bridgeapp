const uuid = require("uuid/v4");
const client = require('../bridge/client');
const { spawn } = require('child_process');

spawn('bridgecs', ['tcp://127.0.0.1:5650', 'tcp://127.0.0.1:5750']);
spawn('bridgecs', ['tcp://127.0.0.1:5660', 'tcp://127.0.0.1:5760']);
spawn('bridgecs', ['tcp://127.0.0.1:5670', 'tcp://127.0.0.1:5770']);
spawn('bridgecs', ['tcp://127.0.0.1:5680', 'tcp://127.0.0.1:5780']);

spawn('bridge', ['--positions', '["north"]', '--connect', '["tcp://localhost:5560","tcp://localhost:5570","tcp://localhost:5580"]', '--cs-cntl', 'tcp://127.0.0.1:5650', '--cs-peer', 'tcp://127.0.0.1:5750', 'tcp://127.0.0.1:5550']);
spawn('bridge', ['--positions', '["east"]', '--connect', '["tcp://localhost:5550","tcp://localhost:5570","tcp://localhost:5580"]', '--cs-cntl', 'tcp://127.0.0.1:5660', '--cs-peer', 'tcp://127.0.0.1:5760', 'tcp://127.0.0.1:5560']);
spawn('bridge', ['--positions', '["south"]', '--connect', '["tcp://localhost:5550","tcp://localhost:5560","tcp://localhost:5580"]', '--cs-cntl', 'tcp://127.0.0.1:5670', '--cs-peer', 'tcp://127.0.0.1:5770', 'tcp://127.0.0.1:5570']);
spawn('bridge', ['--positions', '["west"]', '--connect', '["tcp://localhost:5550","tcp://localhost:5560","tcp://localhost:5570"]', '--cs-cntl', 'tcp://127.0.0.1:5680', '--cs-peer', 'tcp://127.0.0.1:5780', 'tcp://127.0.0.1:5580']);

client('tcp://127.0.0.1:5550').catch((err) => console.log('failed with error:', err));
client('tcp://127.0.0.1:5560').catch((err) => console.log('failed with error:', err));
client('tcp://127.0.0.1:5570').catch((err) => console.log('failed with error:', err));
client('tcp://127.0.0.1:5580').catch((err) => console.log('failed with error:', err));
