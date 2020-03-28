"""
The interface to graphviz, which at the moment, just means running it on the 
command line;
"""

import logging
import subprocess

def runDot(graphvizFilename, outputImageFilename, imageType="png"):
    try: 
        cmd = "dot -T" + imageType + " " + graphvizFilename + " -o" + outputImageFilename

        logging.debug("Running dot like this: %s", cmd)

        output = subprocess.run(cmd.split(" "), shell=False, stderr=True, stdout=True, check=False)

        if output.returncode == 0:
            logging.info("Completed sucessfully, rendered: %s", outputImageFilename)

            return True

        logging.error("dot output: %s", str(output))
    except FileNotFoundError: 
        logging.error("FileNotFoundError. Is the GraphViz's `dot` command installed on your computer? ")

    return False

