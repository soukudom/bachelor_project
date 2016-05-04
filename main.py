#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################
# Author: Dominik Soukup, soukudom@fit.cvut.cz #
################################################

import sys
import os
import argparse
import modules.logic

#exit codes:
#   2: input parameters error
#   5: internal error


#def CheckPrivilege(val):
#    path, name = os.path.split(val)
#    if path == "": path = "."
#    if name == "" or name == ".": name = getDevName(path)
#    try:
#        with open(os.path.join(path, name), mode="w", encoding="utf-8") as f:
#            print("vytvoril jsem soubor", name)
#        os.unlink(os.path.join(path, name))
#    except IsADirectoryError:
#        raise argparse.ArgumentTypeError(
#            "File {} is a directory. Maybe you forgot '/'.".format(name))
#    except PermissionError:
#        raise argparse.ArgumentTypeError(
#            "File {} can not be written to {}.".format(name, path))
#    except Exception as e:
#        print(e)
#        print("vyhodil jsem vyjimku na CheckPrivilege")
#    return os.path.join(path, name)

# \fn checks if the file is usable
# \param val: filename
def checkExist(val):
    if val == None:
        return val
    try:
        with open(val, mode="r") as f:
            pass
    except IsADirectoryError:
        raise argparse.ArgumentTypeError("File {} is a directory.".format(val))
    except PermissionError:
        raise argparse.ArgumentTypeError(
            "File {} can not be opened. Not enough permissions.".format(val))
    except FileNotFoundError:
        raise argparse.ArgumentTypeError("File {} does not exist.".format(val))
    except Exception as e:
        print("Internal error.")
        sys.exit(2)
    return val

#argparser configuration
parser = argparse.ArgumentParser()

parser.add_argument("-cf",
                    "--configFile",
                    help="Device configuration file",
                    type=checkExist,
                    default=None)
parser.add_argument("-df",
                    "--deviceFile",
                    help="File with hosts to configure",
                    type=checkExist,
                    default=None)
parser.add_argument("-sf",
                    "--settingsFile",
                    help="File with global configuration setting",
                    type=checkExist,
                    default=None)
parser.add_argument("-l",
                    "--log",
                    help="File with logs",
                    type=checkExist, 
                    default=None )
parser.add_argument("-p",
                    "--partial",
                    help="Filter for specific group name.",
                    default=None)
parser.add_argument("-pc",
                    "--processCount",
                    help="Number of running processes",
                    default=1)
parser.add_argument("-t",
                    "--timeout",
                    help="Timeout for configuration protocols",
                    default=5)
parser.add_argument("-c",
                    "--community",
                    help="Community string for snmp",
                    default=None)
parser.add_argument("-d",
                    "--debug",
                    help="Debug messages",
                    action="store_true")
                    #default=None)

args = parser.parse_args()

#convert input data to dictionary
data = vars(args)
#call backend object
conf = modules.logic.Orchestrate(data)
