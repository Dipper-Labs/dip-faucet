import os
import json

import tornado

import cfg
import ratelimit
import common


def get_first_arg_name_from_request(request):
    args = request.arguments.keys()
    if len(args) == 1:
        return args[0]
    else:
        return ''


def _assembly_args(data):
    if data.has_key('account'):
        return {'to': data['account'], 'quantity': cfg.SINGLE_GET_TOKEN_AMOUNT}
    else:
        return None


def _os_cmd_transfer(param):
    cmd = 'echo "%s" | dipcli send --from %s --to %s --amount %dpdip -y' % (cfg.FROM_PASSWORD, cfg.FROM_ACCOUNT, param['to'], param['quantity'])
    output = os.popen(cmd).read()
    js = json.loads(output)
    return True, js['txhash']


def _make_transfer(p):
    return _os_cmd_transfer(p)


class GetTokenHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)

    def _handle(self, data):
        param = _assembly_args(data)
        if param:
            ok, tx_hash = _make_transfer(param)
            if ok:
                ratelimit.ip_24h_token_amount_limiter.increase_amount(param['quantity'], self)
                ratelimit.account_24h_token_amount_limiter.increase_amount(1, self)
                common.write_json_response(self, {'msg': 'succeeded', 'tx_hash': tx_hash})
            else:
                msg = {'msg': 'transaction failed, possible reason: account does not exist'}
                common.write_json_response(self, msg, 400)
        else:
            msg = {'msg': 'please use request with URL of format: http://xxxx.org/get_token?valid_account_address'}
            common.write_json_response(self, msg, 400)

    @ratelimit.limit_by(ratelimit.ip_24h_token_amount_limiter)
    @ratelimit.limit_by(ratelimit.account_24h_token_amount_limiter)
    def get(self):
        data = {'account': get_first_arg_name_from_request(self.request)}
        self._handle(data)
