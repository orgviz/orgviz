#!/usr/bin/env python3

import cherrypy

import configargparse
import os

import logging
import sys

from lib import generateDot

parser = configargparse.ArgumentParser(default_config_files = ["~/.orgviz-spreadsheet-reader-web.cfg"])
parser.add_argument("--logging", type = int, default = 20, help = "1 = Everything. 50 = Critical only.", env_var = "LOGGING")
parser.add_argument('--port', default = 8081, type = int, env_var = "PORT");
args = parser.parse_args();

class FrontendWrapper:
    @cherrypy.expose
    def index(self):
        return '<h1>orgviz Spreadsheet Reader</h1>'

    @cherrypy.expose
    def generateDot(self, spreadsheetId="none"):
        try:
            cherrypy.response.headers['Content-Type'] = 'text/plain'

            ret = generateDot(spreadsheetId)

            return ret
        except Exception as e:
            print(str(e))
            raise cherrypy.HTTPError(status=400)

cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': args.port,
    'log.screen': False
});

logging.getLogger().setLevel(args.logging)
logging.basicConfig(format = "[%(levelname)s] %(message)s ")

config = {}

cherrypy.quickstart(FrontendWrapper(), '/', config)

