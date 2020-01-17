#!/usr/bin/env python3

from configargparse import ArgParser
import json
import sys
import logging
import tempfile
import subprocess
import os

def getArgumentParser():
    parser = ArgParser(default_config_files = ["~/.orgviz.cfg"])
    parser.add_argument("--input", "-I", default = "default.org", env_var = "ORGVIZ_INPUT")
    parser.add_argument("--skipDrawingLegend", "-L", action = "store_true")
    parser.add_argument("--skipDrawingTeams", action = "store_true")
    parser.add_argument("--dotout", action = "store_true")
    parser.add_argument("--logging", type = int, default = 20, help = "1 = Everything. 50 = Critical only.")
    parser.add_argument("--teams", nargs = "*", default = [])
    parser.add_argument("--influence", nargs = "*", default = [], choices = ["supporter", "promoter", "enemy", "internal"])
    parser.add_argument("--profilePictureDirectory", default = "/opt/profilePictures/", help = "A directory containing [name].jpeg files of people in your organization.")
    parser.add_argument("--profilePictures", "-P", action = "store_true")
    parser.add_argument("--outputType", "-T", default = "svg", choices = ["png", "svg"])
    parser.add_argument("--keepDotfile", action = "store_false")

    return parser

class Person():
    def __init__(self, fullName):
        self.fullName = fullName.strip()
        self.dotNodeName = convertHumanNameToDotNodeName(fullName)
        self.team = "??"
        self.jobTitle = "??"
        self.influence = ""

    def setInfluence(self, influence):
        self.influence = influence.strip()

    def getRecord(self):
        profilePic = ""

        if args.profilePictures:
            pic = args.profilePictureDirectory + self.fullName + ".jpeg"

            if (os.path.exists(pic)):
                logging.debug("Found LinkedIn profile: " + pic)
                profilePic = '<TABLE BORDER="0"><TR><TD><IMG SRC = "' + pic + '" /></TD></TR></TABLE>|'
            else:
                logging.warning("No profile pic found for " + pic)

        return '<{<B>' + self.fullName + '</B>|' + profilePic  + '<FONT POINT-SIZE="9">Title: ' + self.jobTitle + ' </FONT>}>'

    def setTeam(self, team):
        self.team = team

class Model():
    def __init__(self):
        self.title = "Untitled Organization"
        self.people = dict()
        self.edges = []
        self.teams = set()

    def addPerson(self, personFullName):
        person = Person(personFullName)

        self.people[person.dotNodeName] = person
        self.lastPerson = person

    def addTeam(self, team):
        self.teams.add(team)

    def addConnection(self, edgeType, destination):
        self.edges.append({
            "origin": self.lastPerson.dotNodeName,
            "type": edgeType,
            "destination": convertHumanNameToDotNodeName(destination)
        })

def getFileContents():
    logging.info("Reading file: " + args.input)

    try: 
        f = open(args.input, 'r');

        contents = f.read();

        f.close()

        return contents
    except FileNotFoundError:
        logging.fatal("Could not find input file: " + args.input);
        sys.exit()

def parseModel(contents):
    model = Model()

    for line in contents.split("\n"):
        if line == "": continue

        if line.startswith("@") and ":" in line:
            line = line.replace("@", "")
            key, val = line.split(":", 1)

            if key == "title": model.title = val.strip()

            continue;

        if line.startswith("\t"):
            line = line.strip().replace("\t", "")

            if "->" in line:
                parseConnection(model, line)
                continue

            if ":" in line:
                parsePersonProperty(model, line)
                continue

            logging.warning("Cannot parse line: " + line)


        model.addPerson(line)

    return model

def parseConnection(model, line):
    edgeType, destination = line.split("->", 1)

    if edgeType != "" and destination != "":
        model.addConnection(edgeType.strip(), destination.strip())

def parsePersonProperty(model, line):
    propertyKey, propertyValue = line.split(":", 1)
    propertyKey = propertyKey.strip()
    propertyValue = propertyValue.strip()

    if propertyKey == "influence":
        model.lastPerson.setInfluence(propertyValue)
        return

    if propertyKey == "team":
        model.addTeam(propertyValue)
        model.lastPerson.setTeam(propertyValue)
        return

    if propertyKey == "title":
        model.lastPerson.jobTitle = propertyValue
        return

    logging.warning("Could not parse person property line:" + line)

def convertHumanNameToDotNodeName(name):
    name = name.strip().replace(" ", "_")

    return name

def getInfluenceStyleAsDot(influence):
    if influence == "supporter": return "fillcolor=skyblue, style=filled"
    if influence == "promoter": return 'fillcolor=GreenYellow, style=filled'
    if influence == "enemy": return "fillcolor=salmon, style=filled"
    if influence == "internal": return "fillcolor=black, style=filled, fontcolor=white"
    if influence.strip() == "": return "fillcolor=white, style=filled";

    logging.warning("unknown class: " + influence)

    return ""

def getLegendAsDot():
    out = ""

    if not args.skipDrawingLegend:
        out = ""
        out += "subgraph cluster_00 {\n"
        out += "label=Legend\n"
        out += "fillcolor=beige\n"
        out += "style=filled\n"
        out += "node [fontsize=9]\n"
        out += "supporter [fillcolor=skyblue, style=filled]\n"
        out += "promoter [fillcolor=GreenYellow, style=filled]\n"
        out += "enemy [fillcolor=salmon, style=filled]\n"
        out += "internal [fillcolor=black, fontcolor = white, style=filled]\n"
        out += "}\n"

    return out

def isPersonExcluded(person):
    if len(args.teams) > 0 and person.team not in args.teams:
        return True

    if len(args.influence) > 0 and person.influence not in args.influence:
        return True

    return False

def getTeamsAsDot(model):
    if args.skipDrawingTeams:
        return ""

    out = ""

    subGraphCount = 0;

    # A useful behavior of dot, is that is a subgraph is empty (ie, no nodes), 
    # then it's rendering is skipped. This is why we blindly define all teams 
    # (subgraphs), and only check if people are exclued. 

    for teamName in model.teams:
        subGraphCount += 1

        out += "subgraph cluster_" + str(subGraphCount) + "{\n"
        out += 'label=' + teamName + "\n"
        out += "style=filled\n"
        out += "fillcolor=gray\n"

        for person in model.people.values():
            if isPersonExcluded(person): continue
            if person.team == teamName:
                out += person.dotNodeName + " []\n"

        out += "}\n"

    return out

def getEdgeDotStyle(edge):
    if edge['type'] == "supports":
        return "style=dotted"
    else:
        return ""

def getModelAsDot(model):
    out = ""
    out += "digraph {\n"
    out += 'label="' + model.title + ' - github.com/jamesread/orgviz"' + "\n"
    out += 'labelloc="t"' + "\n"
    out += 'fontname=Overpass' + "\n"
    out += "node [fontname=Overpass, shape=record]\n"
    out += "edge [fontname=Overpass, fontsize=9]\n"

    out += getTeamsAsDot(model)

    for person in model.people.values():
        if isPersonExcluded(person): continue

        out += person.dotNodeName + ' [label=' + person.getRecord() + ']' + "\n"

    for person in model.people.values():
        if isPersonExcluded(person): continue

        out += ("%s [%s]\n") % (person.dotNodeName, getInfluenceStyleAsDot(person.influence))

    for edge in model.edges:
        if isPersonExcluded(model.people[edge['origin']]) or isPersonExcluded(model.people[edge['destination']]): continue

        out += ('%s -> %s [label="%s", %s]' % (edge['origin'], edge['destination'], edge['type'], getEdgeDotStyle(edge))) + "\n"

    out += getLegendAsDot()
    out += "}"
    
    return out

def main():
    global args
    args = getArgumentParser().parse_args()

    logging.getLogger().setLevel(args.logging)
    logging.basicConfig(format = "[%(levelname)s] %(message)s ")

    logging.debug("Teams: " + str(args.teams))

    out = getModelAsDot(parseModel(getFileContents()))

    if args.dotout:
        logging.warning("Outputting graph to stdout, not running Dot")

        print(out)
    else:
        with tempfile.NamedTemporaryFile(delete = args.keepDotfile) as tmp:
            tmp.write(bytes(out, "UTF-8"))
            tmp.flush();

            logging.debug("Wrote DOT file to: " + str(tmp.name));

            outputImageFilename = os.getcwd() + "/orgviz." + args.outputType
            
            cmd = "dot -T" + args.outputType + " " + str(tmp.name) + " -o" + outputImageFilename

            logging.debug("Running dot like this: " + cmd)

            output = subprocess.run(cmd.split(" "), shell = False, stderr = True, stdout = True)

            if output.returncode == 0:
                logging.info("Completed sucessfully, rendered: " + outputImageFilename)

            else:
                logging.error("dot output: " + str(output))

            tmp.close()

if __name__ == "__main__":
    main();

