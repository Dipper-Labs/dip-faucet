#
# code based on https://github.com/nirtayeb/rate-limiter/blob/master/ratelimit.py
#

import redis
import functools

import cfg
import common


g_redis = redis.StrictRedis(db=0)
ip_24h_token_amount_limiter = None
account_24h_token_amount_limiter = None


class RateLimitType:
    def __init__(self, name, amount, expire, identity=lambda h: None, on_exceed=lambda h: None):
        self.name = name
        self.amount = amount
        self.expire_within = expire
        self.identity = identity
        self.on_exceed = on_exceed

    def server_name(self, identity_arg):
        return "l_%s:%s" % (self.name, self.identity(identity_arg))

    def check(self, identity_arg):
        amount = g_redis.get(self.server_name(identity_arg))
        return amount != None and int(amount) >= self.amount

    def update_amount(self, amount, identity_arg, reset_ex=False):
        name = self.server_name(identity_arg)
        if (reset_ex):
            g_redis.set(name, amount, self.expire_within)
        else:
            expire_within = g_redis.ttl(name)
            g_redis.set(name, amount, expire_within)

    def increase_amount(self, amount, identity_arg):
        name = self.server_name(identity_arg)
        print name
        current = g_redis.get(name)
        if current is not None:
            g_redis.incr(name, amount)
        else:
            g_redis.set(name, amount, self.expire_within)


def limit_by(limiter):
    def rate_limiter_decorator(func):
        @functools.wraps(func)
        def func_wrapper(self, *args, **kargs):
            if not limiter.check(self):
                return func(self, *args, **kargs)
            limiter.on_exceed(self)

        return func_wrapper

    return rate_limiter_decorator


def ip_limit_exceed(handler):
    common.write_json_response(handler, {'msg': 'reach 24 hours max token amount'}, 403)


def account_limit_exceed(handler):
    common.write_json_response(handler, {'msg': 'reach 24 hours max account amount'}, 403)


if __name__ == "ratelimit":
    ip_24h_token_amount_limiter = RateLimitType(
        name="ip_24h_token_amount",
        amount=cfg.TOTAL_GET_TOKEN_AMOUNT_PER_IP_24H,
        expire=3600 * 24,  # 24 hours
        identity=lambda h: h.request.remote_ip,
        on_exceed=ip_limit_exceed)

    account_24h_token_amount_limiter = RateLimitType(
        name="account_24h_token_amount",
        amount=cfg.TOTAL_GET_TOKEN_COUNT_PER_ACCOUNT_24H,
        expire=3600 * 24,  # 24 hours
        identity=lambda h: h.request.arguments.keys()[0] if len(h.request.arguments.keys()) == 1 else '',
        on_exceed=account_limit_exceed)