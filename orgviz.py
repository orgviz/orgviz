#!/usr/bin/env python3

from configargparse import ArgParser
import json
import sys
import logging
import tempfile
import subprocess
import os
import re

def getArgumentParser():
    parser = ArgParser(default_config_files = ["~/.orgviz.cfg"])
    parser.add_argument("--input", "-I", default = "default.org", env_var = "ORGVIZ_INPUT")
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
    parser.add_argument("--attributeMatches", "-a", nargs = "*", default = [], metavar = "KEY=VALUE")

    return parser

class Person():
    def __init__(self, fullName):
        fullName = fullName.strip()

        if re.fullmatch("[\w ]+", fullName) == None:
            logging.warn("Person's name contains invalid characters: " + fullName);

        self.fullName = fullName
        self.dotNodeName = convertHumanNameToDotNodeName(fullName)
        self.team = "??"
        self.influence = ""
        self.dmu = "Decision Maker?"
        self.sentiment = "Sentiment?"
        self.attributes = dict();

    def setInfluence(self, influence):
        self.influence = influence.strip()

    def setTeam(self, team):
        self.team = team

    def hasAttribute(self, key):
        return key in self.attributes

    def getAttribute(self, key):
        if key in self.attributes:
            return self.attributes[key]

        return "??"

    def setAttribute(self, k, v):
        self.attributes[k] = v

class Model():
    def __init__(self):
        self.title = "Untitled Organization"
        self.people = dict()
        self.edges = []
        self.teams = set()

    def getPersonByName(self, personFullName):
        if personFullName in self.people:
            return self.people[personFullName]

        raise Exception("Person not found: " + personFullName)

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
    propertyKey = propertyKey.strip().lower()
    propertyValue = propertyValue.strip()

    if propertyKey == "influence":
        model.lastPerson.setInfluence(propertyValue)
        return

    if propertyKey == "sentiment":
        model.lastPerson.sentiment = propertyValue 
        return

    if propertyKey == "dmu":
        model.lastPerson.dmu = propertyValue 
        return

    if propertyKey == "team":
        model.addTeam(propertyValue)
        model.lastPerson.setTeam(propertyValue)
        return

    model.lastPerson.setAttribute(propertyKey, propertyValue)

def convertHumanNameToDotNodeName(name):
    name = name.strip().replace(" ", "_")

    return name

def getInfluenceStyleAsDot(influence):
    if args.vizType == "none": return "fillcolor=white, style=filled"

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
        if args.vizType == "DS":
            pass
        
        if args.vizType == "inf":
            out += "subgraph cluster_00 {\n"
            out += "label=Legend\n"
            out += "fillcolor=beige\n"
            out += "style=filled\n"
            out += "node [fontsize=9]\n"
            out += "supporter [fillcolor=skyblue, style=filled]\n"
            out += "promoter [fillcolor=GreenYellow, style=filled]\n"
            out += "hostile [fillcolor=salmon, style=filled]\n"
            out += "internal [fillcolor=black, fontcolor = white, style=filled]\n"
            out += "}\n"

    return out

def isPersonExcluded(person):
    if len(args.attributeMatches) > 0: 
        for attributeSearch in args.attributeMatches:
            if "=" not in attributeSearch: continue

            key, val = map(lambda i: i.strip(), attributeSearch.split("=", 1))

            if val not in person.getAttribute(key):
                return True

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
        out += 'label="' + teamName + '"' + "\n"
        out += "style=filled\n"
        out += "fillcolor=skyblue\n"

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

def getStyleForDmu(dmu, fullName):
    if dmu == "D": return "green"
    if dmu == "I": return "blue"
    if dmu == "G": return "red"

    logging.warning("Unknown `dmu` (decision maker) for: " + fullName + ", got: " + dmu + ", but should be [D]ecision Maker, [I]nfluencer or [G]atekeeper")

    return "white"

def getStyleForSentiment(sentiment, fullName):
    if sentiment == "P": return "green";
    if sentiment == "N": return "yellow";
    if sentiment == "O": return "red";

    logging.warning("Unknown `sentiment` for: " + fullName + ", got: " + sentiment + ", but should be [P]romoter, [O]pponent or [N]eutral")

    return "white"

def getDsVisType(person):
    ret = '<tr><td bgcolor = "%s" border = "1">%s</td><td bgcolor = "%s" border = "1">%s</td></tr>' % (
        getStyleForDmu(person.dmu, person.fullName),
        person.dmu, 
        getStyleForSentiment(person.sentiment, person.fullName),
        person.sentiment
    )
    return ret

def getPersonLabelAsDot(person):
    ret = '<<table border = "0" cellspacing = "0">';
    ret += '<tr><td border = "1" colspan = "2">%s</td></tr>' % person.fullName
    ret += '<tr><td border = "1" colspan = "2"><font point-size = "9">%s</font></td></tr>' % person.getAttribute("title")

    profilePic = ""

    if args.profilePictures:
        pic = args.profilePictureDirectory + person.fullName + ".jpeg"

        if (os.path.exists(pic)):
            logging.debug("Found LinkedIn profile: " + pic)

            ret += '<tr><td colspan = "2" border = "1"><img src = "%s" /></td></tr>' % pic
        else:
            logging.warning("No profile pic found for " + pic)

    if person.hasAttribute("country"):
        ret += '<tr><td colspan = "2">' + person.getAttribute('country')  +  '</td></tr>'

    if args.vizType == "DS":
        ret += getDsVisType(person)

    ret += "</table>>"
    return ret;


def getModelAsDot(model):
    out = ""
    out += "digraph {\n"

    if args.outputType == "png":
        out += "graph [ dpi = 300 ]\n"

    if not args.skipDrawingTitle:
        out += 'label="' + model.title + ' - github.com/jamesread/orgviz"' + "\n"

    out += 'labelloc="t"' + "\n"
    out += 'fontname=Overpass' + "\n"
    out += "node [fontname=Overpass, shape=record]\n"
    out += "edge [fontname=Overpass, fontsize=9]\n"

    out += getTeamsAsDot(model)

    for person in model.people.values():
        if isPersonExcluded(person): continue

        out += ("%s [margin=0, border=invisible, label=%s,%s]\n") % (person.dotNodeName, getPersonLabelAsDot(person), getInfluenceStyleAsDot(person.influence))

    for edge in model.edges:
        if isPersonExcluded(model.getPersonByName(edge['origin'])) or isPersonExcluded(model.getPersonByName(edge['destination'])): continue

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

