#!/usr/bin/env python3

import cherrypy

import configargparse
import os

import logging
import sys

sys.path.insert(0, "./orgviz")

from orgviz.modelToGraphviz import ModelToGraphVizConverter
from orgviz.model import ModelOptions
from orgviz.modelParser import parseModel
from orgviz.graphviz import runDot

parser = configargparse.ArgumentParser(default_config_files = ["~/.orgviz-web.cfg"])
parser.add_argument("--logging", type = int, default = 20, help = "1 = Everything. 50 = Critical only.")
parser.add_argument('--port', default = 8081, type = int);
parser.add_argument('--outputDirectoryLocal', default = "/var/www/html/orgvizOutput/");
parser.add_argument('--outputDirectoryPublic', default = "http://localhost:8081/output/");
args = parser.parse_args();

class FrontendWrapper:
    @cherrypy.expose
    def index(self):
        return '<h1>orgviz API!</h1><p>Hi! Did you want the <a href = "webui">webui</a>?'

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def createImageFromOrgViz(self):
        errors = list();
        body = cherrypy.request.body.read().decode('utf-8')
        dotOutput = False

        if len(body) == 0:
            errors.append("Error: No content")
        else:
            opts = ModelOptions()
            opts.skipDrawingLegend = True
            opts.skipDrawingTitle = True

            conv = ModelToGraphVizConverter(opts=opts)
            mdl = parseModel(body)
            body = conv.getModelAsDot(mdl)

            f = open("/tmp/orgfile", "w")
            f.write(body);
            f.close()

            dotOutput = runDot("/tmp/orgfile", args.outputDirectoryLocal + "/orgviz.png")


        if dotOutput and len(errors) == 0:
            print("Dot ran okay")

            return {
                "errors": list(),
                "filename": args.outputDirectoryPublic + "orgviz.png" 
            }
        else:
            return {
                "errors": errors,
                "filename": None
            }


cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': args.port,
    'log.screen': False
});

config = {
    '/webui': {
    'tools.staticdir.on': True,
    'tools.staticdir.dir': 'webui/dist/',
    'tools.staticdir.root': os.path.abspath(os.getcwd()),
    'tools.staticdir.index': 'index.html'
    },
    '/output': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': args.outputDirectoryLocal,
        'tools.expires.on': True,
        'tools.expires.secs': 1,
    }
}

logging.getLogger().setLevel(args.logging)
logging.basicConfig(format = "[%(levelname)s] %(message)s ")

cherrypy.quickstart(FrontendWrapper(), '/', config)

