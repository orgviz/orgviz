#!/usr/bin/env python3

import cherrypy

import configargparse
import os

from time import sleep

import logging
import sys

from lib import generateDot, getSheetsApi, setCredentialsJson

parser = configargparse.ArgumentParser(default_config_files = ["~/.spreadsheet-reader-web.cfg"])
parser.add_argument("--logging", type = int, default = 20, help = "1 = Everything. 50 = Critical only.", env_var = "LOGGING")
parser.add_argument("--credentialsJson", default = '/etc/orgviz/spreadsheet-reader-credentials.json', env_var = 'CREDENTIALS_JSON')
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

def setupCredentialsJson():
    # Design choice: sleep-wait for the file, as containers might take a short
    # time to "mount" the configuration file, or it might not be configured, 
    # and without it the app will just crash/exit later. Hence, sleep-wait 
    # instead if hard-fail-fast.

    while not os.path.exists(args.credentialsJson):
        logging.info("Credentials file does not exist, expected it here: " + args.credentialsJson)
        sleep(10)

    logging.info("Found credentials file: " + args.credentialsJson)

    setCredentialsJson(args.credentialsJson)

    # Behavior: Get the sheets API here (and do nothing with it) so that the 
    # first "real" request does not stall while the login flow is completed.

    getSheetsApi()

cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': args.port,
    'log.screen': False
});

logging.getLogger().setLevel(args.logging)
logging.basicConfig(format = "[%(levelname)s] %(message)s ")

config = {}

setupCredentialsJson()

cherrypy.quickstart(FrontendWrapper(), '/', config)
