#!/usr/vin/env python3
# -*- coding: utf-8 -*-

#Author: Dominik Soukup, soukudom@fit.cvut.cz
#!!!pohrat si z chybovymi vypisy
#!!!upravit vypisovy hlasky aby byly konkretnejsi, a vypisovat je na chybovej vystup a s lepsim formatovanim
import getpass
import sys
import os
import modules.factory as factory
import importlib
import modules.connect as connect
from paramiko.ssh_exception import AuthenticationException
from multiprocessing import Pool, Process, Manager
import time

#exit codes:
#   1: file formating error
#   2: file/parameter missing error
#   3: closed by user 

def createDefName():
    defName = "log.txt"
    number = 0
    content = os.listdir("./")
    while defName in content:
        defName = "log" + str(number + 1).zfill(3) + ".txt"
        number += 1
    try:
        with open(defName, encoding="utf-8", mode="w") as f:
            pass
    except Exception as e:
        print("Can not create '{}' file.".format(defName))
        return None
    return defName


class Orchestrate:
    def __init__(self, arguments):
        #finding out settings file filename
        factory_tmp = factory.Factory()     #creation factory object  
        self.configuration = {}             #dictionary with device configuration data
        self.protocol = {}                  #dictionary with data necessary for configuration protocols
        self.conn = None                    #connection handler
        #self.partial = arguments["partial"] #name for group filtering

        if arguments["settingsFile"]:
            self.settingsFile = arguments["settingsFile"]    #settings filename with global configuration data
            self.globalSettings = factory_tmp.getSettingsProcessing(
                self.settingsFile
            )                                   #creation settings parse object from factory
            self.globalSettings.parse("")       
        
            if type(self.globalSettings.settingsData) != type(dict()):
                print("Error: Bad settings file '{}' format.".format(self.settingsFile))
                #self.write2log("Bad settings file format. Please read manual for help.")
                sys.exit(1)

        if not arguments["partial"]:
            try:
                self.partial = self.globalSettings.settingsData["partial"]
            except KeyError as e:
                #print("Error: Config file has not been inserted.") 
                #sys.exit(2)
                self.partial = None
            except AttributeError as e:
                #print("Error: Unable to get compulsory config data")
                #sys.exit(2)
                self.partial = None
        else:
            self.partial = arguments["partial"] #name for group filtering

        #Checking data from settings file. Data from command line has higher priority
        if not arguments["configFile"]:
            try:
                configFile = self.globalSettings.settingsData["configFile"]
            except KeyError as e:
                print("Error: Config file has not been inserted.")
                #self.write2log("Config file has not been inserted. It is necessary to specify filename in settings file or in commandline.")
                sys.exit(2)
            except AttributeError as e:
                print("Error: Unable to get compulsory config data")
                sys.exit(2)
        else:
            configFile = arguments["configFile"]

        if not arguments["deviceFile"]:
            try:
                deviceFile = self.globalSettings.settingsData["deviceFile"]
            except KeyError as e:
                print("Error: Device file has not been inserted.")
                #self.write2log("Device file has not been inserted. It is necessary to specify filename int settings file or in commandline")
                sys.exit(2)
            except AttributeError as e:
                print("Error: Unable to get compulsory config data")
                sys.exit(2)
        else:
            deviceFile = arguments["deviceFile"]

        if not arguments["log"]:
            try:
                self.logFile = self.globalSettings.settingsData["log"]
            except KeyError as e:
                print("Log file has not been inserted")
                print("Creating default log file...")
                self.logFile = createDefName()
                if not self.logFile:
                    print("Can not create log file.")
                    sys.exit(2)
                print("Log file '{}' has been created.".format(self.logFile))
            except AttributeError as e:
                print("Error: Unable to get compulsory config data")
                sys.exit(2)
                    
        else:
            self.logFile = arguments["log"]

        if arguments["processCount"] == 1:
            try:
                self.process_count = self.globalSettings.settingsData[
                    "processCount"]
            except KeyError as e:
                self.process_count = 1
            except AttributeError as e:
                self.process_count = 1
        else:
            self.process_count = arguments["processCount"]

        if arguments["timeout"] == 5:
            try:
                self.protocol["timeout"] = self.globalSettings.settingsData[
                    "timeout"]
            except KeyError as e:
                self.protocol["timeout"] = 5
            except AttributeError as e:
                self.protocol["timeout"] = 5
        else:
            self.protocol["timeout"] = arguments["timeout"]

        if not arguments["community"]:
            try:
                self.protocol["community"] = self.globalSettings.settingsData[
                    "community"]
            except KeyError as e:
                print("Error: Community string has not been inserted.")
                sys.exit(2)
            except AttributeError as e:
                print("Error: Unable to get compulsory config data")
                sys.exit(2)
        else:
            self.protocol["community"] = arguments["community"]

        if arguments["debug"] == None:
            try:
                self.debug = self.globalSettings.settingsData["debug"]
            except KeyError as e:
                self.debug = None
            except AttributeError as e:
                print("Error: Unable to get compulsory config data")
                sys.exit(2)
        else:   
            self.debug = arguments["debug"]

        #sets credentials to access network devices
        self.setCredentials()

        try:
            self.device = factory_tmp.getDeviceProcessing(
                deviceFile
            )                               #creation device parse object from factory
        except Exception as e:
            print("Error: Can not get device parse object from factory. Check the log file.")
            self.write2log(str(e))
            sys.exit(2)
            
        try:
            self.config = factory_tmp.getConfigProcessing(
                configFile
            )                               #creation configuraton parse object from factory
        except Exception as e:
            print("Error: Con not get configuration parse object from factory. Check the log file")
            self.write2log(str(e))
            sys.exit(2)

        #prepare configuration data for configuring
        self.buildConfiguration()
        #run configuration
        self.doConfiguration()

    def setCredentials(self):
        username = input("Type your username:")             #username for authentication
        password = getpass.getpass("Type your password:")   #password for authentication
        #save gained data to protocol dictionary
        self.protocol["username"] = username
        self.protocol["password"] = password

    def buildConfiguration(self):
        try:
            methods = self.config.parse("")  #parse configuration file
        except Exception as e:
            print(e)
            print("Error during parsing configuration file. Check the log file.")
            self.write2log(str(e))
            sys.exit(1)

        #basic data type check
        if type(methods) != type(list()):
            print("Error during parsing configuration file. Check the log file.")
            self.write2log("Return type must be list not {}".format(type(methods)))
            sys.exit(1)

        #goes through all method and prepare it for paralel processing
        for method in methods:
            print(method) #!!! print
            #partial filtering
            if not self.partial in method and self.partial != None:
                print("preskakuju")
                continue
            try:
                #parse device file with concrete groupname
                #hosts format is {vendor: list(ip_addresses)}
                hosts = self.device.parse(method[0])
                print("cilovy hosti",hosts)
            except Exception as e:
                print("Error during parsing device file. Check the log file.")
                self.write2log(str(e))
                sys.exit(1)

            #basic datatype check
            if type(hosts) != type(dict()):
                print("Error during parsing device file. Check the log file.")
                self.write2log("Return type must be dict not {}".format(type(hosts)))
                sys.exit(1)
                
            #finds out the name of device module which is needed for dynamic import
            for vendor in hosts:
                #basic datatype check
                if type(hosts[vendor]) != type(list()):
                    print("Error during parsing device file. Check the log file.")
                    self.write2log("Return type must be in format {vendor: list(ip_addresses)}")
                    sys.exit(1)

                for host in hosts[vendor]:
                    #prepares necessary information for snmp protocol
                    self.protocol["ip"] = host
                    self.protocol["method_type"] = "get"
                    #returns name of manufactor module
                    manufactor = self.getManufactor(vendor)
                    #manufactor datatype check
                    if type(manufactor) != type(list()):
                        self.write2log("Bad format of manufactor name structure: '{}'".format(manufactor))
                        manufactor = None
                    elif len(manufactor) != 2:
                        self.write2log("Not enough data field in manufactor structure. Vendor and device type is needed.")
                        manufactor = None

                    if manufactor == None:
                        print(
                            "Getting manufactor name of '{}' no success".format(
                                host))
                        option = input(
                            "Would you like to go to next device? [Y/n]")
                        if option == "Y":
                            continue
                        else:
                            print("Closing configuration...")
                            self.write2log("Configuration closed by user.")
                            sys.exit(3)

                    #appends ip address of device to vendor name structure 
                    manufactor.append(host)
                    #convert list data type to tuple due to hash ability
                    manufactor = tuple(manufactor)
                    #append method to concrete devices, this structure is good for pararel processing
                    try:
                        self.configuration[manufactor].append(method)
                    except:
                        self.configuration[manufactor] = [method]
            print(self.configuration)

    def getManufactor(self, vendor):
        #imports default parse class for specific vendor
        module = "device_modules.{}.{}".format(vendor, vendor)
        #import main vendor module
        try:
            importObj = importlib.import_module(module)
        except ImportError as e:
            print("Error during importing '{}'".format(module))
            self.write2log("Name of manufactor module '{}' does not exist.".format(module))
            return None
        #import default class about vendor devices
        try:
            obj = getattr(importObj, "Device")
        except AttributeError as e:
            print("Class 'Device' in '{}' module does not exist".format(vendor))
            self.write2log("Class 'Device' in '{}' module does not exist".format(vendor)) 
            return None

        #creates instance of Device class
        objInst = obj()
        #calls getDeviceName method to get device module name
        try:
            manufactor = objInst.getDeviceName(self.protocol)
        except AttributeError as e:
            print("Method 'getDeviceName' does not exist in '{}' device module".format(vendor))
            self.write2log("Method 'getDeviceName' does not exist in '{}' device module".format(vendor))
            return None
        return manufactor


    def connect2device(self, conn_method):
        #finds out the type of connection method
        conn = getattr(connect, conn_method)
        self.conn = conn(self.protocol)
        try:
            self.conn.connect()
        except Exception as e:
            print("Unable to connect to the network device. Check log.")

            self.write2log(
                "Authentication failed. Connection protocol '{}'".format(conn_method))
            return "Authentication failed.","Unknown",self.protocol["ip"]

    #changes connection method according to device module value
    def makeChange(self,conn_method, config_method):
        #default is hybrid or auto and manual is needed 
        if (self.config_method_def == "hybrid" or
                self.config_method_def == "auto") and config_method == "manual":
            self.conn = self.conn.disconnect()
        #default is manual and hybrid or auto is needed
        elif (config_method == "hybrid" or
              config_method == "auto") and self.config_method_def == "manual":
            r = self.connect2device(conn_method)
            if r:
                return (4,r)
        #default is hybrid or auto and hybrid or auto is needed (different procol can be used)
        elif (config_method == "hybrid" or config_method == "auto") and (
                self.config_method_def == "hybrid" or self.config_method_def == "auto"):
            #check possible protocol change
            if self.conn_method_def != conn_method:
                self.conn = self.conn.disconnect()
                r = self.connect2device(conn_method)
                if r:
                    return (4,r)
        else:
            #return connection back if default method was auto or hybrid
            if self.conn == None and self.config_method_def == "auto" or self.config_method_def == "hybrid":
                r = self.connect2device(self.conn_method_def)
                if r:
                    return (4,r)
                
            return (0,self.conn_method_def, self.config_method_def)
    
        return (0,conn_method,config_method)
    def printResult(self,result):
        #!!!pouzit naky specialni direktiry proto
        print("*"*20)
        for res in result:
            print("*"*5)
            print("Device: {}".format(res[1]))
            print("Ip address: {}".format(res[2]))
            print("Status: {}".format(res[0]))
            print("*"*5)
        
        print("*"*20)
        

    def doConfiguration(self):
        number_of_devices = len(self.configuration) #number of devices ready to be configured
        cnt = 0 #help variable for checking number of progress dots
        print("Number of devices:", number_of_devices)
        #in case of higher number of processes the devices, that processes are unnecessary
        if number_of_devices < int(self.process_count):
            self.process_count = number_of_devices
        print("Number of proceses: {}\n".format(self.process_count))
        #preparing pararel configuration
        p = Pool(processes=int(self.process_count))
        m = Manager()
        #preparing input arguments
        args = [i for i in self.configuration]
        #devices are independed so pool is random
        result = p.map_async(self.configureDevice, args)
        #checking configuration progress
        while True:
            cnt += 1
            if result.ready():
                break
            else:
                if not self.debug:
                    dots = (cnt%4)
                    if dots == 0:
                        print("\033[1AConfiguring devices. Please wait   \033[0m")
                
                    else:
                        print("\033[1AConfiguring devices. Please wait{}\033[0m".format("."*dots))
                    #speed of progress dots
                    time.sleep(0.3)
        output = result.get()
        self.printResult(output)
        #result codes:
            #1: Missing compulsory atributes 'method' and 'connection' in 'DefaultConnection' class
            #2: Device module does not return any configuration data
            #3: Configuration method is not valid, is not form set (auto, manual, hybrid)
            #4: Connection problem
            #5: Unable do command

    def write2log(self, message):
        try:
            #opens log file and writes message
            with open(self.logFile, encoding="utf-8", mode="a") as log:
                log.write(message)
                log.write("\n")

        except Exception as e:
            print("Error: unable to access to log file '{}'".format(self.logfile))

    def configureDevice(self, dev):
        self.conn_method_def = None     #default connection method
        self.config_method_def = None   #default configuration method
        conn_method = None              #local connection method
        config_method = None            #local configuration method
        self.protocol["ip"] = dev[2]    #ip refresh #!!!uprava kvuli kontrolovani prubehu, zkontrolovat

        #gets and checks default connection and configuration data
        importObj = self.importDefault(dev)
        #error occured
        if type(importObj) == type(int()):
            if importObj == 1:
                return "Missing compulsory values.",dev[1],self.protocol["ip"]
            #return importObj

        #connect to the device according to the method
        if self.config_method_def == "auto" or self.config_method_def == "hybrid":
            r = self.connect2device(self.conn_method_def)
            if r:
                return r

        #goes throught all method and configurates them
        for method in self.configuration[dev]:
            #prints progress of configuration
            if not self.debug:
                print(" "*36,"\033[1A\033[0K: Configuring {} at device {}".format(method[1],dev[1]))
            #class import
            objInst = self.classImport(importObj,method,dev)
            #error occured
            if type(objInst) == type(int()):
                #return objInst
                return "Missing compulsory values.",dev[1],self.protocol["ip"]
    
            #finds out local connect and configuration values, these values are unnecessary
            try:
                conn_method = objInst.method
                config_method = objInst.connection
            except AttributeError:
                pass
            #changes connection settings according to local conf. and connect values
            tmp = self.makeChange(conn_method,config_method)
            if tmp[0] != 0:
                print("Error: Error during changing configuration method.")
                self.write2log("Unable to change connection and configuration method. Error in makeChange method.")
                return tmp[1]

            conn_method = tmp[1]
            config_method = tmp[2]

        #imports method or submethod for auto configuration module
        #auto is automatic configuration without Protocol structure
            if config_method == "auto":
                ret = self.importAuto(objInst,method,dev)
                #an error occured
                if ret == 1:
                    return "Missing compulsory values.",dev[1],self.protocol["ip"]
                elif ret == 2:
                    return "Device module does not return any configuration data.",dev[1],protocol["ip"]
                elif ret == 5:
                    return "Unable to do command.",dev[1], self.protocol["ip"]

            #if config method is manual or hybrid, dictionary Protocol is sent to device module
            elif config_method == "manual" or config_method == "hybrid":
                ret = self.importWithProtocol(objInst,method,dev,config_method)
                #error occured
                if ret == 1:
                    return "Missing compulsory values.",dev[1],self.protocol["ip"]
                elif ret == 2:
                    return "Device module does not return any configuration data.",dev[1],protocol["ip"] 
            else:
                #return 3
                return "Configuration method is not valid.",dev[1], self.protocol["ip"]

            #reset local connection and configuration settings
            conn_method = None
            config_method = None
            if self.config_method_def == "manual" and self.conn != None:
                self.conn = self.conn.disconnect()
        #final disconnection and result return
        try:
            if self.conn != None: 
                self.conn.disconnect()
            return "OK",dev[1],self.protocol["ip"]
        except Exception as e:
            print("Error: Problem during disconnecting.")
            return "Closing session problem.",dev[1],self.protocol["ip"]

    def classImport(self,importObj,method,dev):
        #call method class
        try:
            obj = getattr(importObj, method[1])
        except AttributeError as e:
            print("\nError: Module 'device_module/{}/{}' has not class '{}'".format(
                dev[0], dev[1], method[1]))
            self.write2log("Module 'device_module/{}/{}' has not class '{}''".format(dev[0],dev[1],method[1]))
            print("\nClosing device connection...")
            self.conn.disconnect()
            return 1

        objInst = obj()

        return objInst


    def importAuto(self,objInst,method,dev):
        #configurint submethod
        if method[3]:
            try:
                inst = getattr(objInst, method[3])
            except Exception as e:
                print(
                    "Object '{}' has no method '{}'. Check file 'device_modules/{}/{}'".format(
                        method[1], method[3], dev[0], dev[1]))
                self.write2log(
                    "Object '{}' has no method '{}'. Check file 'device_modules/{}/{}'".format(
                        method[1], method[3], dev[0], dev[1]))
                print("Closing device connection...")
                self.conn.disconnect()
                return 1

            try:
                deviceSet = inst(**method[-1])
            except TypeError as e:
                arg = str(e).split()
                print("Method '{}' has no argument {}".format(method[
                    3], arg[-1]))
                self.write2log("Method '{}' has no argument {}".format(method[
                    3], arg[-1]))
                print("Closing device connection.")
                self.conn.disconnect()
                return 1
        #configuring method
        else:
            try:
                inst = getattr(objInst, method[2].strip())
            except Exception as e:
                print(
                    "Object '{}' has no method '{}'. Check file 'device_modules/{}/{}'".format(
                        method[1], method[2], dev[0], dev[1]))
                self.write2log("Object '{}' has no method '{}'. Check file 'device_modules/{}/{}'".format(
                         method[1], method[2], dev[0], dev[1]))
                print("Closing device connection.")
                self.conn.disconnect()
                return 1
            try:
                deviceSet = inst(**method[-1])
            except TypeError as e:
                arg = str(e).split()
                print("Method '{}' has no argument {}".format(method[
                    2], arg[-1]))
                self.write2log("Method '{}' has no argument {}".format(method[
                    2], arg[-1]))
                print("Closing device connection.")
                self.conn.disconnect()
                return 1
        #checks if deviceSet (list of network device command) are empty
        #these command are returned by device module
        if deviceSet == None:
            self.conn.disconnect()
            return 2
        try:
            self.conn.doCommand(deviceSet,self.debug)
        except Exception as e:
            print("Error: Unable to do commands. Check log.")
            self.write2log(str(e))
            return 5

        return None

    def importWithProtocol(self,objInst,method,dev,config_method):
        #configuring submethod
        if method[3]:
            try:
                inst = getattr(objInst, method[3])
            except Exception as e:
                print("Object '{}' has no method '{}'. Check file 'device_module/{}/{}'".format(method[1],method[3],dev[0],dev[1]))
                self.write2log("Object '{}' has no method '{}'. Check file 'device_module/{}/{}'".format(method[1],method[3],dev[0],dev[1]))
                #hybrid connection has established connection, so it must be disconnected
                if config_method == "hybrid":
                    print("Closing device connection.")
                    self.conn.disconnect()
                return 1
            #append protocol structure
            method[-1]["protocol"] = self.protocol
            try:
                deviceSet = inst(**method[-1])
            except TypeError as e:
                arg = str(e).split()
                print("Method '{}' has no argument {}".format(method[3],arg[-1]))
                self.write2log("Method '{}' has no argument {}".format(method[3],arg[-1]))
                #same reason like above
                if config_method == "hybrid":
                    print("Closing device connection.")
                    self.conn.disconnect()
                return 1
        #configuring method
        else: #!!! pocitam s tim ze je pouze method a submethod, osetrit aby se nemohlo stat nic jinyho
            try:
                inst = getattr(objInst, method[2].strip())
            except Exception as e:
                print("Object '{}' has no method '{}'. Check file 'device_module/{}/{}'".format(method[1],method[2],dev[0],dev[1]))
                self.write2log("Object '{}' has no method '{}'. Check file 'device_module/{}/{}'".format(method[1],method[2],dev[0],dev[1]))
                if config_method == "hybrid":
                    print("Closing device connection.")
                    self.conn.disconnect()
                return 1
            #almost same like above in submethod configuring 
            method[-1]["protocol"] = self.protocol
            try:
                deviceSet = inst(**method[-1])
            except Exception as e:
                arg = str(e).split()
                print("Method '{}' has no argument {}".format(method[2],arg[-1]))
                self.write2log("Method '{}' has no argument {}".format(method[2],arg[-1]))
                if config_method == "hybrid":
                    print("Closing device connection.")
                    self.conn.disconnect()
                return 1

        if config_method == "hybrid":
            if deviceSet == None:
                self.conn.disconnect()
                print("Closing device connection...")
                return 2
            try:
                self.conn.doCommand(deviceSet,self.debug)
            except Exception as e:
                print("Error: Unable to do commands.")
                self.write2log(str(e))
                return 1
        return None

    def importDefault(self,dev):
        #build device modul name for import
        module = "device_modules.{}.{}".format(dev[0], dev[1])
        try:
            importObj = importlib.import_module(module)
        except ImportError as e:
            print("Error during importing defaut device module '{}'".format(module))
            self.write2log("Device module '{}' does not exits".format(module))
            return 1
        #imports default class to get default configuratin device data
        try:
            obj = getattr(importObj, "DefaultConnection")
        except AttributeError as e:
            print("Class 'DefaultConnection' in device module is compulsory.")
            print("Go to the next device...")
            self.write2log("Missing compulsory class 'DefaultConnection' in device module.")
            return 1
        objInst = obj()
        try:
            self.conn_method_def = objInst.method
            self.config_method_def = objInst.connection
        except AttributeError:
            print(
                "Atributes 'method' and 'connection' in class 'DefaultConnection' are compulsory")
            print("Go to to the next device")
            self.write2log("Missing compulsory data 'method' and 'connection' in class 'DefaultConnection'")
            return 1

        return importObj
