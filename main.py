import os
import sys

import tornado.ioloop
import tornado.web
import tornado.httpserver

import cfg
import handler


def make_app():
    return tornado.web.Application([
        (r"/dip/get_token", handler.GetTokenHandler),
    ])


if __name__ == "__main__":
    cfg.FROM_PASSWORD = raw_input("enter from account password:\n")

    pid = os.fork()
    if pid > 0:
        sys.exit(0)

    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(cfg.PORT)
    server.start(0)
    tornado.ioloop.IOLoop.current().start()
