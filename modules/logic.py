#!/usr/vin/env python3

import getpass
import sys
import os
import modules.factory as factory
import importlib
import modules.connect as connect
from paramiko.ssh_exception import AuthenticationException
from multiprocessing import Pool, Process


def createDefName():
    defName = "log.yml"
    number = 0
    content = os.listdir("./")
    while defName in content:
        defName = "log" + str(number + 1).zfill(3) + ".yml"
        number += 1
    try:
        with open(defName, encoding="utf-8", mode="w") as f:
            pass
    except Exception as e:
        print("Can not create '{}' file.".format(defname))
        return defname
       # sys.exit(1)


class Orchestrate:
    def __init__(self, arguments):

        #deviceFile #nazev konfiguracniho souboru pro zarizeni
        #configFile #nazev konfiguracniho souboru pro nastaveni
        if not arguments["settingsFile"]:
            print(
                "Settings file not specyfied. Using default name: 'setting.yml'")
            settingsFile = "setting.yml"
        else:
            settingsFile = arguments["settingsFile"]

        self.settingsFile = settingsFile  #nazev konfiguracniho souboru pro globalni parametry
        self.factory = factory.Factory()  # vytvoreni objektu tovarny
        self.configuration = {
        }  # slovnik obsahujici konfiguraci, ktera se bude volat
        self.protocol = {
        }  # slovnik, kterej bude slouzit pro data pro protokoly
        self.conn = None  #connection handler
        self.partial = arguments["partial"]

        self.globalSettings = self.factory.getSettingsProcessing(
            self.settingsFile
        )  #vytvoreni objektu pro parsovani globalniho nastaveni
        self.globalSettings.parse("")
        if type(self.globalSettings.settingsData) != type(dict()):
            print("Bad settings file format. Please read manual for help.")
            sys.exit(1)
        #ulozeni nazvu konfiguranich souboru; prednost maji prepinace pred konfiguracnim souborem
        if not arguments["configFile"]:
            try:
                configFile = self.globalSettings.settingsData["config_file"]
            except KeyError as e:
                print("Config file has not been inserted.")
                self.write2log("Config file has not been inserted.")
                sys.exit(1)
        else:
            configFile = arguments["configFile"]

        if not arguments["deviceFile"]:
            try:
                deviceFile = self.globalSettings.settingsData["device_file"]
            except KeyError as e:
                print("Device file has not been inserted")
                self.write2log("Device file has not been inserted.")
                sys.exit(1)
        else:
            deviceFile = arguments["deviceFile"]

        if not arguments["log"]:
            try:
                self.logFile = self.globalSettings.settingsData["log_file"]
            except KeyError as e:
                print("Log file has not been inserted")
                print("Creating default log file")
                r = createDefName()
                if r:
                    print("Can not create '{}' file.".format(r))
                    self.write2log("Can not create '{}' file.".format(r))
                    sys.exit(1)
                    
        else:
            self.logFile = arguments["log"]
        if arguments["numberOfProcess"] == 1:
            try:
                self.process_count = self.globalSettings.settingsData[
                    "process_count"]
            except KeyError as e:
                self.process_count = 1
        else:
            self.process_count = arguments["numberOfProcess"]
        if arguments["timeout"] == 5:
            try:
                self.protocol["timeout"] = self.globalSettings.settingsData[
                    "timeout"]
            except KeyError as e:
                self.protocol["timeout"] = 5
        else:
            self.protocol["timeout"] = arguments["timeout"]
        if not arguments["community"]:
            try:
                self.protocol["community"] = self.globalSettings.settingsData[
                    "community_string"]
            except KeyError as e:
                print("Community string has not been inserted.")
                self.write2log("Community string has not been inserted.")
                sys.exit(1)
        else:
            self.protocol["community"] = arguments["community"]

        print(self.protocol["timeout"])
        self.setCredentials()
        #self.protocol["community"] = self.globalSettings.settingsData["community_string"]
        #self.protocol["timeout"] = self.globalSettings.settingsData["timeout"]

        try:
            self.device = self.factory.getDeviceProcessing(
                deviceFile
            )  #vytvoreni objektu pro parsovani konfiguracniho souboru zarizeni
        except Exception as e:
            print("Problem with getting config parse object from factory.")
            print(e)
            self.write2log(str(e))
            sys.exit(1)
            
        try:
            self.config = self.factory.getConfigProcessing(
                configFile
            )  
        except Exception as e:
            print("Problem with getting config parse object from factory.")
            print(e)
            self.write2log(str(e))
            sys.exit(1)

        self.buildConfiguration()
        self.doConfiguration()

    def setCredentials(self):
        username = input("Type your username:"
                         )  #username pro prihlaseni na zarizeni
        password = getpass.getpass("Type your password:"
                                   )  #password pro prihlaseni
        self.protocol["username"] = username
        self.protocol["password"] = password

    def buildConfiguration(self):
        try:
            methods = self.config.parse("")  # parsovani konfiguraniho souboru
        except Exception as e:
            print("vyjimka pri parsovani configu")
            print(e)
            self.write2log(str(e))
            sys.exit(1)

        print("naparsoval jsem", methods)

        for method in methods:
            if not self.partial in method:
                continue
            print("najdi jmeno pro", method[0])
            try:
                hosts = self.device.parse(
                    method[0])  # zjisti zarizeni, ktere se budou nastavovat
            except Exception as e:
                print("vyjimka pri parsovani devicu")
                print(e)
                self.write2log(str(e))
                sys.exit(1)

            print("budu nastavovat", hosts)
            for vendor in hosts:  # zjisti nazev zarizeni, ktery je potrebny pro dynamickou praci
                for host in hosts[vendor]:
                    #pripraveni ip a method_type pro protokol
                    self.protocol["ip"] = host
                    self.protocol["method_type"] = "get"
                    #manufactor = self.device.getManufactor(self.protocol,vendor)
                    manufactor = self.getManufactor(vendor)
                    #pokud snmp neziskal data tak se pokracuje dal
                    if manufactor == None:
                        print(
                            "Getting manufactor name of '{}' no success".format(
                                host))
                        option = input(
                            "Would you like to go to next device? [Y/n]")
                        if option == "Y":
                            continue
                        else:
                            print("Closing netat configuration")
                            sys.exit(1)

                        #podarilo se ziskat vyrobce, uklada se do slovniku
                    print("vyrobce", vendor, " je", manufactor)
                    manufactor.append(host)
                    manufactor = tuple(manufactor)
                    try:
                        self.configuration[manufactor].append(method)
                    except:
                        self.configuration[manufactor] = [method]

                    #continue

    def getManufactor(self, vendor):
        #import defaultni parsovaci tridy
        module = "device_modules.{}.{}".format(vendor, vendor)
        importObj = importlib.import_module(module)
        obj = getattr(importObj, "Device")
        objInst = obj()
        manufactor = objInst.getDeviceName(self.protocol)
        return manufactor

    def connect2device(self, conn_method):
        #pripoj se na zarizeni
        conn = getattr(connect, conn_method)
        self.conn = conn(self.protocol)
        #while True:
        try:
            #conn.connect(dev[2],self.protocol)
            self.conn.connect()
           # break
        except Exception as e:
            #except AuthenticationException as e:
            print(e)
            print("Closing netat configuration due to connect")

            self.write2log(
                "Authentication failed. Username: {}, Password: {}".format(
                    self.protocol["username"], self.protocol["password"]))
            print("navrat")
            return "Authentication failed."
            #sys.exit(1)

                #zmeni spojeni se zarizenim podle device modulu
    def makeChange(self, conn_method_def, config_method_def, conn_method,
                   config_method):
        #pokud je nastaven hybrid nebo auto a jdu na manual
        if (config_method_def == "hybrid" or
                config_method_def == "auto") and config_method == "manual":
            self.conn.disconnect()
        #pokud je nastaven manual a je hybrid nebo auto
        elif (config_method == "hybrid" or
              config_method == "auto") and config_method_def == "manual":
            r = self.conn.connect2device(conn_method)
            if r:
                return (1,r)
        #pokud jdu z hybrid nebo auto na to samy
        elif (config_method == "hybrid" or config_method == "auto") and (
                config_method_def == "hybrid" or config_method_def == "auto"):
            #kontrola jestli se nezmenil protokol a neni treba prepojit
            if conn_method_def != conn_method:
                self.conn.disconnect()
                r = self.conn.connect2device(conn_method)
                if r:
                    return (1,r)
        else:
            return (0,conn_method_def, config_method_def)

        return (0,conn_method,config_method)

    def doConfiguration(self):
        #print("pocet procesu {}".format(self.globalSettings.settingsData["process_count"]))
        number_of_devices = len(self.configuration)
        print("pocet zarizeni", number_of_devices)
        if number_of_devices < int(self.process_count):
            self.process_count = number_of_devices
        print("pocet procesu {}".format(self.process_count))

        pool = Pool(processes=int(self.process_count))
        results = [pool.apply_async(self.configureDevice,
                                    args=(dev, ))
                   for dev in self.configuration]
        output = [p.get() for p in results]
        print(output)
        #for dev in self.configuration:
        #    retCode = self.configureDevice(dev)
        #    if retCode == 1:
        #        print("Missing compulsory atributes 'method' and 'connection' in 'DefaultConnection' class")
        #        print("Go to the next device...")
        #        continue

        #   elif retCode == 2:
        #       print("Device module does not return any configuration data")
        #       print("Go to the next device...")
        #       continue

        #  elif retCode == 3:
        #      print("Configuration method is not valid")
        #      print("Go to the next device")
        #      continue

    def write2log(self, message):
        try:
            with open(self.logFile, encoding="utf-8", mode="a") as log:
                log.write(message)
                log.write("\n")

        except Exception as e:
            #print(e)
            print("write2log error")#!!!mozna osetrit i kdyz se nepovede zapsat do logu

    def configureDevice(self, dev):
        conn_method_def = None
        config_method_def = None
        conn_method = None
        config_method = None
        self.protocol["ip"] = dev[2]

        #sestaveni modulu pro import
        module = "device_modules.{}.{}".format(dev[0], dev[1])
        importObj = importlib.import_module(module)
        try:
            obj = getattr(importObj, "DefaultConnection")
        except AttributeError as e:
            print("Class 'DefaultConnection' in device module is compulsory")
            print("Go to the next device")
            return 1
        objInst = obj()
        try:
            conn_method_def = objInst.method
            config_method_def = objInst.connection
        except AttributeError:
            print(
                "Atributes 'method' and 'connection' in class DefaultConnection are compulsory")
            print("Go to to the next device")
            return 1

        #pripoj se na zarizeni
        if config_method_def == "auto" or config_method_def == "hybrid":
            r = self.connect2device(conn_method_def)
            if r:
                return r

            #projdi vsechny metody pro dany zarizeni
        for method in self.configuration[dev]:
            #zavolani tridy
            try:
                obj = getattr(importObj, method[1])
            except AttributeError as e:
                print("Module 'device_module/{}/{}' has not class '{}'".format(
                    dev[0], dev[1], method[1]))
                #option = input("Would you like to continue?[Y/n]")
                #if option == "Y" or option == "y":
                #    continue
                #else:
                print("Closing device connection.")
                self.conn.disconnect()
                #sys.exit(1)
                return 1

            objInst = obj()

            #zjisteni protokolu spojeni tady uz to je nepovinny
            try:
                conn_method = objInst.method
                config_method = objInst.connection
            except AttributeError:
                pass
            #kontrola zmen parametru pro pripojeni
            tmp = self.makeChange(conn_method_def, config_method_def,
                                  conn_method, config_method)
            if tmp[0] != 0:
                print("chyba v makeChange")
                return tmp[0]

            conn_method = tmp[1]
            config_method = tmp[2]

            #pokud nebylo defaultni nastaveni upraveno, tak ho pouzij
            #!!!nejsem si jistej jestli se to pouziva
            if conn_method == None:
                conn_method = conn_method_def
            if config_method == None:
                config_method = config_method_def

            if config_method == "auto":
                #pokud se nastavuje submethod
                if method[3]:
                    try:
                        inst = getattr(objInst, method[3])
                    except Exception as e:
                        print(
                            "Object '{}' has no method '{}'. Check file 'device_modules/{}/{}'".format(
                                method[1], method[3], dev[0], dev[1]))
                        #option = input("Would you like to continue?[Y/n]")
                        #if option == "Y" or option == "y":
                        #    continue
                        #else:
                        print("Closing device connection.")
                        self.conn.disconnect()
                        #sys.exit(1)
                        return 1

                    try:
                        deviceSet = inst(**method[-1])
                    except TypeError as e:
                        arg = str(e).split()
                        print("Method '{}' has no argument {}".format(method[
                            3], arg[-1]))
                        #option = input("Would you like to continue?[Y/n]")
                        #if option == "Y" or option == "y":
                        #    continue
                        #else:
                        print("Closing device connection.")
                        self.conn.disconnect()
                        #sys.exit(1)
                        return 1
                #pouze method
                else:
                    try:
                        inst = getattr(objInst, method[2].strip())
                    except Exception as e:
                        print(
                            "Object '{}' has no method '{}'. Check file 'device_modules/{}/{}'".format(
                                method[1], method[2], dev[0], dev[1]))
                        #option = input("Would you like to continue?[Y/n]")
                        #if option == "Y" or option == "y":
                        #    continue
                        #else:
                        print("Closing device connection.")
                        self.conn.disconnect()
                        #sys.exit(1)
                        return 1
                    try:
                        deviceSet = inst(**method[-1])
                    except TypeError as e:
                        #print(e) #!!! smazat
                        arg = str(e).split()
                        print("Method '{}' has no argument {}".format(method[
                            2], arg[-1]))
                        #option = input("Would you like to continue?[Y/n]")
                        #if option == "Y" or option == "y":
                        #    continue
                        #else:
                        print("Closing device connection.")
                        self.conn.disconnect()
                        #sys.exit(1)
                        return 1

                if deviceSet == None:
                    self.conn.disconnect()
                    return 2
                try:
                    self.conn.doCommand(deviceSet)
                except Exception as e:
                    print(e)
                    self.write2log(str(e))
            #pokud je to manual nebo hybrid tak posilam navim self.protocol
            elif config_method == "manual" or config_method == "hybrid":
                #pokud se nastavuje submethod
                if method[3]:
                    try:
                        inst = getattr(objInst, method[3])
                    except Exception as e:
                        print("Object '{}' has no method '{}'. Check file 'device_module/{}/{}'".format(method[1],method[3],dev[0],dev[1]))
                        if config_method == "hybrid":
                            print("Closing device connection.")
                            self.conn.disconnect()
                        return 1
                    method[-1]["protocol"] = self.protocol
                    try:
                        deviceSet = inst(**method[-1])
                    except TypeError as e:
                        arg = str(e).split()
                        print("Method '{}' has no argument {}".format(method[3],arg[-1]))
                        if config_method == "hybrid":
                            print("Closing device connection.")
                            self.conn.disconnect()
                        return 1
                #pouze method
                else: #!!! pocitam s tim ze je pouze method a submethod, osetrit aby se nemohlo stat nic jinyho
                    try:
                        inst = getattr(objInst, method[2].strip())
                    except Exception as e:
                        print("Object '{}' has no method '{}'. Check file 'device_module/{}/{}'".format(method[1],method[2],dev[0],dev[1]))
                        if config_method == "hybrid":
                            print("Closing device connection.")
                            self.conn.disconnect()
                        return 1
                        
                    method[-1]["protocol"] = self.protocol
                    try:
                        deviceSet = inst(**method[-1])
                    except Exception as e:
                        arg = str(e).split()
                        print("Method '{}' has no argument {}".format(method[2],arg[-1]))
                        if config_method == "hybrid":
                            print("Closing device connection.")
                            self.conn.disconnect()
                        return 1

                if config_method == "hybrid":
                    if deviceSet == None:
                        self.conn.disconnect()
                        return 2
                    try:
                        self.conn.doCommand(deviceSet)
                    except Exception as e:
                        print(e)
                        self.write2log(str(e))
                        return 1

            else:
                return 3

            #resetuj nastaveni pro conn a config
            conn_method = None
            config_method = None
        try:
            self.conn.disconnect()
            return "ok"
        except Exception as e:
            print("nastala vyjimka")
            return 1
