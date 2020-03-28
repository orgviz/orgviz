#!/usr/bin/env python3

from configargparse import ArgParser
import sys
import logging
import tempfile
import os

import sys

sys.path.insert(0, "./orgviz")

from orgviz.modelToGraphviz import ModelToGraphVizConverter
from orgviz.modelParser import parseModel
from orgviz.model import ModelOptions
from orgviz.graphviz import runDot

def getArgumentParser():
    parser = ArgParser(default_config_files = ["~/.orgviz.cfg"])
    parser.add_argument("--input", "-I", default = "default.org", env_var = "ORGVIZ_INPUT")
    parser.add_argument("--output", "-O", default = os.getcwd())
    parser.add_argument("--skipDrawingLegend", "-L", action = "store_true")
    parser.add_argument("--skipDrawingTeams", action = "store_true")
    parser.add_argument("--skipDrawingTitle", action = "store_true")
    parser.add_argument("--dotout", action = "store_true")
    parser.add_argument("--logging", type = int, default = 20, help = "1 = Everything. 50 = Critical only.")
    parser.add_argument("--teams", nargs = "*", default = [])
    parser.add_argument("--influence", nargs = "*", default = [], choices = ["supporter", "promoter", "enemy", "internal"])
    parser.add_argument("--profilePictureDirectory", default = "/opt/profilePictures/", help = "A directory containing [name].jpeg files of people in your organization.")
    parser.add_argument("--profilePictures", "-P", action = "store_true")
    parser.add_argument("--outputType", "-T", default = "svg", choices = ["png", "svg"])
    parser.add_argument("--keepDotfile", action = "store_false")
    parser.add_argument("--vizType", choices = ["DS", "inf", "none"], default = "DS");
    parser.add_argument("--dpi", type = int, default = 100, help = 'DPI (resolution), only used for PNG.');
    parser.add_argument("--attributeMatches", "-a", nargs = "*", default = [], metavar = "KEY=VALUE")

    return parser

def getFileContents():
    logging.info("Reading org file: " + args.input)

    try: 
        f = open(args.input, 'r');

        contents = f.read();

        f.close()

        return contents
    except FileNotFoundError:
        logging.fatal("Could not find input file: " + args.input);
        sys.exit()

def main():
    global args
    args = getArgumentParser().parse_args()

    logging.getLogger().setLevel(args.logging)
    logging.basicConfig(format = "[%(levelname)s] %(message)s ")

    logging.debug("Teams: " + str(args.teams))

    opts = ModelOptions();
    opts.skipDrawingLegend = args.skipDrawingLegend
    opts.skipDrawingTitle = args.skipDrawingTitle
    opts.skipDrawingTeams = args.skipDrawingTeams
    opts.vizType = args.vizType
    opts.outputType = args.outputType
    opts.teams = args.teams
    opts.attributeMatches = args.attributeMatches
    opts.influence = args.influence
    opts.profilePictures = args.profilePictures
    opts.profilePictureDirectory = args.profilePictureDirectory
    opts.dpi = args.dpi

    mdl = parseModel(getFileContents())
    converter = ModelToGraphVizConverter(opts);

    out = converter.getModelAsDot(mdl);

    if args.dotout:
        logging.warning("Outputting graph to stdout, not running Dot")

        print(out)
    else:
        temporaryGraphvizFile = tempfile.NamedTemporaryFile(delete = args.keepDotfile)
        temporaryGraphvizFile.write(bytes(out, "UTF-8"))
        temporaryGraphvizFile.flush();

        logging.debug("Wrote DOT file to: " + str(temporaryGraphvizFile.name));

        outputImageFilename = args.output + "/orgviz." + args.outputType
        
        runDot(str(temporaryGraphvizFile.name), outputImageFilename, args.outputType)

        temporaryGraphvizFile.close() # will delege the org file if !args.keepDotFile

if __name__ == "__main__":
    main();

