const { sendCommand, parseCommandReply } = require('./utils.js');

module.exports = function(sock, command, args) {
    return new Promise(function(resolve, reject) {
        console.log('command:', command, args);
        sock.once("message", function() {
            const reply = parseCommandReply(arguments);
            console.log('reply:', reply);
            if (reply.status >= 0 && reply.command == command) {
                resolve(reply);
            } else {
                reject(reply);
            }
        });
        sendCommand(sock, command, args);
    });
};
