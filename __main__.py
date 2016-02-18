#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import modules.logic

#return codes:
#   1: chyba prepinacu


def getDefName(path):
    defName = "log.yml"
    number = 0
    content = os.listdir(path)
    while defName in content:
        defName = "devices" + str(number + 1).zfill(3) + ".yml"
        number += 1
    return defName


def CheckPrivilege(val):
    path, name = os.path.split(val)
    if path == "": path = "."
    if name == "" or name == ".": name = getDevName(path)
    try:
        with open(os.path.join(path, name), mode="w", encoding="utf-8") as f:
            print("vytvoril jsem soubor", name)
        os.unlink(os.path.join(path, name))
    except IsADirectoryError:
        raise argparse.ArgumentTypeError(
            "File {} is a directory. Maybe you forgot '/'.".format(name))
    except PermissionError:
        raise argparse.ArgumentTypeError(
            "File {} can not be written to {}.".format(name, path))
    except Exception as e:
        print(e)
        print("vyhodil jsem vyjimku na CheckPrivilege")
    return os.path.join(path, name)


def CheckExist(val):
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
        print("vyhazuju vyjimku CheckExist")
        print(e)
    return val


parser = argparse.ArgumentParser()
#subparsers = parser.add_subparsers()
#
##pridat nacitani ze souboru, z radky bude mit vetsi planost 
#
##scanovani
#subparser_scan = subparsers.add_parser("scan",help="scan network device file")
##parametr nazev vystupniho souboru
#subparser_scan.add_argument("-f","--file",help="output device file", type=CheckPrivilege,default="")
#subparser_scan.add_argument("-s","--setting",help="program settings file", type=CheckExist,default="")
#
#
#konfigurace
#subparser_config = subparsers.add_parser("config", help="config devices")
#parametr nazev kofiguraku
#subparser_config.add_argument("-f","--file",help="device config description", type=CheckExist, default="")
#parametr nazev konfiguraku:cast
#subparser_config.add_argument("-p","--part", help="partial configuration")
#subparser_config.add_argument("-c","--clean",help="clean old configuration", action="store_true")
#subparser_config.add_argument("-s","--setting",help="program settings file", type=CheckExist, default="")
#subparser_config.add_argument("-d","--device",help="device file config", type=CheckExist, default="")
#

parser.add_argument("-cf",
                    "--configFile",
                    help="device configuration file",
                    type=CheckExist,
                    default=None)
parser.add_argument("-df",
                    "--deviceFile",
                    help="file with hosts to configure",
                    type=CheckExist,
                    default=None)
parser.add_argument("-sf",
                    "--settingsFile",
                    help="file with global setting configuration",
                    type=CheckExist,
                    default=None)
parser.add_argument("-l",
                    "--log",
                    help="log file",
                    type=getDefName,
                    default=None)
parser.add_argument("-p",
                    "--partial",
                    help="choose one group from config file",
                    default="")
parser.add_argument("-np",
                    "--numberOfProcess",
                    help="specify number of process",
                    default=1)
parser.add_argument("-t",
                    "--timeout",
                    help="specify timeout for network connection",
                    default=5)
parser.add_argument("-c",
                    "--community",
                    help="community string for snmp",
                    default=None)

args = parser.parse_args()
#pokud neni zadoni nic, tak vyhodit help
#if len(sys.argv) == 1:
#    parser.print_help()
#    sys.exit(1)

print(args)

data = vars(args)

#conf = modules.logic.Orchestrate(data["device"],data["file"],data["setting"],data["log"],data["devPart"],data["configPart"])
conf = modules.logic.Orchestrate(data)
#conf.buildConfiguration()
#conf.doConfiguration()
