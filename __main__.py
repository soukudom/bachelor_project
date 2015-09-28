#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import modules.wrap

#return codes:
#   1: chyba prepinacu

def getDevName(path):
    defName = "devices.yml"
    number = 0
    content = os.listdir(path)
    while defName in content:
        defName = "devices" + str(number+1).zfill(3) + ".yml" 
        number += 1
    return defName
         
    
    
def CheckPrivilege(val):
    #if val == None:
    #    val = "."
    path, name = os.path.split(val)
    if path == "": path = "."
    if name == "" or name == ".": name = getDevName(path)
    try:
        with open(os.path.join(path,name),mode="w",encoding="utf-8") as f:
            #pass
            print("vytvoril jsem soubor", name)
        os.unlink(os.path.join(path,name))
    except IsADirectoryError:
        raise argparse.ArgumentTypeError("File {} is a directory. Maybe you forgot '/'.".format(name))
    except PermissionError:
        raise argparse.ArgumentTypeError("File {} can not be written to {}.".format(name,path))
    except Exception as e:
        print(e)
        print("vyhodil jsem vyjimku na CheckPrivilege")
    return os.path.join(path,name)
    

def CheckExist(val):
    try:
        with open(val, mode="r") as f:
            pass
    except IsADirectoryError:
        raise argparse.ArgumentTypeError("File {} is a directory.".format(val))
    except PermissionError:
        raise argparse.ArgumentTypeError("File {} can not be opened. Not enough permissions.".format(name,path))
    except FileNotFoundError:
        raise argparse.ArgumentTypeError("File {} does not exist.".format(val))
    except Exception as e:
        print("vyhazuju vyjimku CheckExist")
        print(e)
    return val

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

#pridat nacitani ze souboru, z radky bude mit vetsi planost 

#scanovani
subparser_scan = subparsers.add_parser("scan",help="scan network device file")
#parametr nazev vystupniho souboru
subparser_scan.add_argument("-f","--file",help="output device file", type=CheckPrivilege,default="devices.yml")
subparser_scan.add_argument("-s","--setting",help="program settings file", type=CheckExist,default="setting.txt")

# prida info do databaze
#parser.add_argument("-g","--get_data",help="get device configuration", default=None)

#konfigurace
subparser_config = subparsers.add_parser("config", help="config devices")
#parametr nazev kofiguraku
subparser_config.add_argument("-f","--file",help="device config description", type=CheckExist, default="config.yml")
#parametr nazev konfiguraku:cast
subparser_config.add_argument("-p","--part", help="partial configuration")
subparser_config.add_argument("-c","--clean",help="clean old configuration", action="store_true")
subparser_config.add_argument("-s","--setting",help="program settings file", type=CheckExist, default="setting.txt")
subparser_config.add_argument("-d","--device",help="device file config", type=CheckExist, default="hosts.yml")

args = parser.parse_args()
#pokud neni zadoni nic, tak vyhodit help
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


print(args)

data = vars(args)
#pars = modules.wrap.parseDevice(data["device"])
pars = modules.wrap.parseConfig(data["file"])
pars._parse()
