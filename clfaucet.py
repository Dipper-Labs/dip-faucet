import os
import sys
import json

import tornado.ioloop
import tornado.web
import tornado.httpserver

import cfg
import ratelimit

# runtime input params
FROM_PASSWORD = ""


# ------------------------------------------------------------------------------------------
# ------ token transfer limiter

def token_limit_exceed(handler):
    write_json_response(handler, {'msg': 'reach 24 hours max token amount'}, 403)


def account_limit_exceed(handler):
    write_json_response(handler, {'msg': 'reach 24 hours max account amount'}, 403)


ip_24h_token_amount_limiter = ratelimit.RateLimitType(
    name="ip_24h_token_amount",
    amount=cfg.TOTAL_GET_TOKEN_AMOUNT_PER_IP_24H,
    expire=60,  # 24 hours
    identity=lambda h: h.request.remote_ip,
    on_exceed=token_limit_exceed)

account_24h_token_amount_limiter = ratelimit.RateLimitType(
    name="account_24h_token_amount",
    amount=cfg.TOTAL_GET_TOKEN_COUNT_PER_ACCOUNT_24H,
    expire=60,  # 24 hours
    identity=lambda h: h.request.arguments.keys()[0] if len(h.request.arguments.keys()) == 1 else '',
    on_exceed=account_limit_exceed)


# ------------------------------------------------------------------------------------------
# ------ common functions

def write_json_response(handler, msg, code=200):
    handler.set_status(code)
    handler.set_header('Content-Type', 'application/json; charset=UTF-8')
    handler.write(msg)


def get_first_arg_name_from_request(request):
    args = request.arguments.keys()
    if len(args) == 1:
        return args[0]
    else:
        return ''


# ------------------------------------------------------------------------------------------
# ------ Get Token Handler

class GetTokenHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)

    def _assembly_args(self, data):
        if data.has_key('account'):
            p = {}
            p['to'] = data['account']
            p['quantity'] = cfg.SINGLE_GET_TOKEN_AMOUNT
            return p
        else:
            return None

    def _os_cmd_transfer(self, param):
        cmd = 'echo "%s" |  dipcli send %s %s %dpdip -y' % (FROM_PASSWORD, cfg.FROM_ACCOUNT, param['to'], param['quantity'])
        print cmd
        output = os.popen(cmd).read()
        js = json.loads(output)
        return True, js['txhash']

    def _make_transfer(self, p):
        return self._os_cmd_transfer(p)

    def _handle(self, data):
        param = self._assembly_args(data)
        if param:
            ok, txhash = self._make_transfer(param)
            if ok:
                ip_24h_token_amount_limiter.increase_amount(param['quantity'], self)
                account_24h_token_amount_limiter.increase_amount(1, self)
                print ip_24h_token_amount_limiter.server_name(self)
                print account_24h_token_amount_limiter.server_name(self)
                write_json_response(self, {'msg': 'succeeded', 'txhash': txhash})
            else:
                failmsg = {'msg': 'transaction failed, possible reason: account does not exist'}
                write_json_response(self, failmsg, 400)
        else:
            fmtmsg = {'msg': 'please use request with URL of format: http://xxxx.org/get_token?valid_account_address'}
            write_json_response(self, fmtmsg, 400)

    @ratelimit.limit_by(ip_24h_token_amount_limiter)
    @ratelimit.limit_by(account_24h_token_amount_limiter)
    def get(self):
        data = {'account': get_first_arg_name_from_request(self.request)}
        self._handle(data)


# --------------------------l---------------------------------------------------------------
# ------ service app

def make_app():
    return tornado.web.Application([
        (r"/get_token", GetTokenHandler),
    ])


if __name__ == "__main__":
    cfg.load_cfg()

    FROM_PASSWORD = raw_input("enter from account password:\n")

    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(cfg.PORT)
    server.start(0)
    tornado.ioloop.IOLoop.current().start()
