const _ = require("underscore");
const zmq = require("zeromq");
const command = require("./messaging/command");
const { parseEvent } = require("./messaging/utils.js");

function eventEndpointFromControlEndpoint(controlEndpoint) {
    const idx = controlEndpoint.lastIndexOf(":");
    const prefix = controlEndpoint.substr(0, idx);
    const port = parseInt(controlEndpoint.substr(idx+1));
    return prefix + ":" + (port+1);
}

async function initGame(endpoint, gameUuid, create) {
    const curve_serverkey = Buffer.from("rq:rM>}U?@Lns47E1%kR.o@n%FcmmsL/@{H8]yf7\0");
    const curve_publickey = Buffer.from("Yne@$w-vo<fVvi]a<NY6T1ed:M$fCG*[IaLV{hID\0");
    const curve_secretkey = Buffer.from("D:)Q[IlAW!ahhC2ac:9*A}h:p?([4%wOTJ%JR%cs\0");
    const controlSocket = zmq.socket("req");
    controlSocket.
        setsockopt(zmq.options.curve_serverkey, curve_serverkey).
        setsockopt(zmq.options.curve_publickey, curve_publickey).
        setsockopt(zmq.options.curve_secretkey, curve_secretkey).
        connect(endpoint);
    await command(controlSocket, "bridgehlo", { version: [0], role: "client" });
    var game = gameUuid;
    if (create) {
        game = (await command(controlSocket, "game", { game })).args.game;
    }
    game = (await command(controlSocket, "join", { game })).args.game;
    const eventSocket = zmq.socket("sub");
    eventSocket.
        setsockopt(zmq.options.curve_serverkey, curve_serverkey).
        setsockopt(zmq.options.curve_publickey, curve_publickey).
        setsockopt(zmq.options.curve_secretkey, curve_secretkey).
        subscribe(game).
        connect(eventEndpointFromControlEndpoint(endpoint));
    const position = (await command(
        controlSocket, "get", { game, keys: ["position"]})).args.position;
    return { controlSocket, eventSocket, game, position };
}

function TurnPromise(eventSocket, position) {
    return new Promise(function (resolve, reject) {
        eventSocket.on("message", function _listener () {
            const event = parseEvent(arguments);
            console.log("event:", event);
            if (event.event == "turn" && event.args.position == position) {
                eventSocket.removeListener("message", _listener);
                resolve();
            }
        });
    });
}

async function getActions(controlSocket, game) {
    const reply = await command(controlSocket, "get", {
        game: game, keys: ["allowedCards", "allowedCalls"]});
    return reply.args;
}

function playTurn(controlSocket, game, allowedCards, allowedCalls) {
    if (!_.isEmpty(allowedCards)) {
        return command(controlSocket, "play", {
            game, card: _.sample(allowedCards) });
    } else {
        return command(controlSocket, "call", {
            game, call: _.sample(allowedCalls) });
    }
}

module.exports = async function(endpoint, gameUuid, create) {
    const { controlSocket, eventSocket, game, position } =
              await initGame(endpoint, gameUuid, create);
    var { allowedCards, allowedCalls } = await getActions(controlSocket, game);
    var turnPromise = TurnPromise(eventSocket, position);
    if (!_.isEmpty(allowedCalls) || !_.isEmpty(allowedCards)) {
        await playTurn(controlSocket, game, allowedCards, allowedCalls);
    }
    while (true) {
        await turnPromise;
        ({ allowedCards, allowedCalls } = await getActions(controlSocket, game));
        turnPromise = TurnPromise(eventSocket, position);
        await playTurn(controlSocket, game, allowedCards, allowedCalls);
    }
};
