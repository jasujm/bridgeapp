module.exports = {
    sendCommand: function(sock, command, args) {
        var parts = [command];
        for (key in args) {
            if (args[key] !== undefined) {
                parts.push(key);
                parts.push(JSON.stringify(args[key]));
            }
        }
        sock.send(parts);
    },
    parseCommandReply: function(parts) {
        var reply = {
            status: parts[0] && parts[0].readInt32BE(),
            command: parts[1] && parts[1].toString(),
            args: {}
        };
        for (let i = 2; i+1 < parts.length; i += 2) {
            let key = parts[i].toString();
            let value = JSON.parse(parts[i+1]);
            reply.args[key] = value;
        }
        return reply;
    },
    parseEvent: function(parts) {
        const [game, event] = parts[0].toString().split(":");
        var reply = {
            game: game,
            event: event,
            args: {}
        };
        for (let i = 1; i+1 < parts.length; i += 2) {
            let key = parts[i].toString();
            let value = JSON.parse(parts[i+1]);
            reply.args[key] = value;
        }
        return reply;
    }
};
