#!/usr/bin/env python3

import cherrypy

import orgviz

import configargparse
import os

from orgviz import getModelAsDot

parser = configargparse.ArgumentParser();
parser.add_argument('--port', default = 8081, type = int);
args = parser.parse_args();

class FrontendWrapper:
    @cherrypy.expose
    def index(self):
        return '<h1>orgviz API!</h1><p>Hi! Did you want the <a href = "webui">webui</a>?'

    @cherrypy.expose
    def createImageFromOrgViz(self):
        return "graph"


cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': args.port
});

config = {
    '/webui': {
    'tools.staticdir.on': True,
    'tools.staticdir.dir': 'webui/dist/',
    'tools.staticdir.root': os.path.abspath(os.getcwd()),
    'tools.staticdir.index': 'index.html'
    },
    '/output/': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': '/home/xconspirisist/sandbox/orgviz/',
    }
}

cherrypy.quickstart(FrontendWrapper(), '/', config)

