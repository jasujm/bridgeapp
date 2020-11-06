import { Call } from "./api/types"

export function callKey(call: Call) {
    let ret: Array<string> = [call.type];
    if (call.bid) {
        ret = ret.concat([String(call.bid.level), call.bid.strain]);
    }
    return ret.join("-");
}
