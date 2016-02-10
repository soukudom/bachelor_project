#!/usr/vin/env python3

import getpass
import sys
import os
import modules.factory as factory
import importlib
import modules.connect as connect

class Orchestrate:    
    def __init__(self, deviceFile, configFile, settingsFile ):

        self.deviceFile = deviceFile #nazev konfiguracniho souboru pro zarizeni
        self.configFile = configFile #nazev konfiguracniho souboru pro nastaveni
        self.settingsFile = settingsFile #nazev konfiguracniho souboru pro globalni parametry
        self.factory = factory.Factory() # vytvoreni objektu tovarny
        self.configuration = {} # slovnik obsahujici konfiguraci, ktera se bude volat
        self.protocol={} # slovnik, kterej bude slouzit pro data pro protokoly
        self.conn = None #connection handler

        self.globalSettings = self.factory.getSettingsProcessing(self.settingsFile) #vytvoreni objektu pro parsovani globalniho nastaveni
        self.globalSettings.parse("")
        
        #ulozeni nazvu konfiguranich souboru; prednost maji prepinace pred konfiguracnim souborem
        if not self.configFile: 
            try:
                self.configFile = self.globalSettings.settingsData[config_file]
            except KeyError as e:
                print("Config file has not been inserted")
                sys.exit(1)

        if not self.deviceFile:
            try:
                self.deviceFile = self.globalSettings.settingsData[device_file]
            except KeyError as e:
                print("Config file has not been inserted")
                sys.exit(1)
        
        self.setCredentials()
        self.protocol["community"] = self.globalSettings.settingsData["community_string"]
        
        
        self.device = self.factory.getDeviceProcessing(self.deviceFile) #vytvoreni objektu pro parsovani konfiguracniho souboru zarizeni
        self.config = self.factory.getConfigProcessing(self.configFile) #vytvoreni objektu pro parsovani konfiguracniho souboru pro nastaveni


    def setCredentials(self):
        username = input("Type your username:") #username pro prihlaseni na zarizeni
        password = getpass.getpass("Type your password:") #password pro prihlaseni
        self.protocol["username"] = username
        self.protocol["password"] = password

#        self.credentials = [username,password]
        
    def buildConfiguration(self):
        
        methods = self.config.parse("") # parsovani konfiguraniho souboru

        for method in methods:
            hosts = self.device.parse(method[0]) # zjisti zarizeni, ktere se budou nastavovat         
            for vendor in hosts: # zjisti nazev zarizeni, ktery je potrebny pro dynamickou praci
                for host in hosts[vendor]:
                    #pripraveni ip a method_type pro protokol
                    self.protocol["ip"] = host
                    self.protocol["method_type"] = "get"
                    manufactor = self.device.getManufactor(self.protocol,vendor)
                    #pokud snmp neziskal data tak se pokracuje dal
                    if manufactor == None:
                        print("Getting manufactor name of '{}' no success".format(host))
                        option = input("Would you like to continue? [Y/n]")
                        if option == "Y":
                            continue
                        else:
                            print("Closing netat configuration")
                            sys.exit(1)
                        
                    #podarilo se ziskat vyrobce, uklada se do slovniku    
                    manufactor.append(host)
                    manufactor = tuple(manufactor)
                    try:
                        self.configuration[manufactor].append(method)
                    except:
                        self.configuration[manufactor] = [method]

                    #continue

    def connect2device(self,conn_method):
        #pripoj se na zarizeni
        conn = getattr(connect, conn_method)            
        self.conn = conn(self.protocol)
        #conn._connect(dev[2],self.username,self.password)
        while True:
            try:
                #conn.connect(dev[2],self.protocol)
                self.conn.connect()
                break;
            except Exception as e:
                print(e)
                option = input("Would you like to try it again?[Y/n]")
                if option == "Y":
                    self.setCredentials()
                    continue
                else:
                    print("Closing netat configuration")
                    sys.exit(1)
        #return conn 

    #zmeni spojeni se zarizenim podle device modulu
    def makeChange(self,conn_method_def,config_method_def,conn_method,config_method):
        #pokud je nastaven hybrid nebo auto a jdu na manual
        if (config_method_def == "hybrid" or config_method_def == "auto") and confing_method == "manual":
            self.conn.disconnect()
        #pokud je nastaven manual a je hybrid nebo auto
        elif (config_method == "hybrid" or config_method == "auto") and confing_method_def == "manual":
            self.conn.connect2device(conn_method)
        #pokud jdu z hybrid nebo auto na to samy
        elif (config_method == "hybrid" or config_method == "auto") and (confing_method_def == "hybrid" or config_method_def == "auto"):
            #kontrola jestli se nezmenil protokol a neni treba prepojit
            if conn_method_def != conn_method:
                self.conn.disconnect()
                self.conn.connect2device(conn_method)
                
        return conn_method, config_method                

    def doConfiguration(self):
        conn_method_def = None
        config_method_def = None
        conn_method = None
        config_method = None

        for dev in self.configuration:
            #sestaveni modulu pro import
            module = "device_modules.{}.{}".format(dev[0],dev[1])
            importObj = importlib.import_module(module)
            obj = getattr(importObj,"DefaultConnection") #!!! osetrit pokud trida DefaultConnection nebude existovat  
            objInst = obj()
            try:
                conn_method_def = objInst.method
                config_method_def = objInst.connection
            except AttributeError:
                print("atributes method and connection in class DefaultConnection are compulsory")
                print("Going to next device")
                continue
            
             
            #pripoj se na zarizeni            
            if config_method_def == "auto" or config_method_def == "hybrid":
                self.connect2device(conn_method_def)
                                                                
                print("nastavuju device", dev)
            #projdi vsechny metody pro dany zarizeni
            for method in self.configuration[dev]:
                print("vstupni method je",method)
                #zavolani tridy
                obj = getattr(importObj,method[1])
                objInst = obj()

                #zjisteni protokolu spojeni tady uz to je nepovinny
                try:
                    conn_method = objInst.method
                    config_method = objInst.connection
                    #kontrola zmen parametru pro pripojeni
                    tmp = self.makeChange(conn_method_def,config_method_def,conn_method,config_method)
                    conn_method = tmp[0] 
                    config_method = tmp[1]

                except AttributeError:
                    pass
                    
                #pokud nebylo defaultni nastaveni upraveno, tak ho pouzij
                if conn_method == None:
                    conn_method = conn_method_def
                if config_method == None:
                    config_method = config_method_def 
                    
                if config_method == "auto": 
                    #pokud se nastavuje submethod
                    if method[3]:
                        inst = getattr(objInst,method[3])
                        deviceSet = inst(**method[-1])
                    #pouze method
                    else:
                        inst = getattr(objInst,method[2].strip())
                        deviceSet = inst(**method[-1])

                    if deviceSet == None:
                        self.conn.disconnect()
                        return
                    self.conn.doCommand(deviceSet)

                elif config_method == "manual" or config_method == "hybrid":
                    #pokud se nastavuje submethod
                    if method[3]:
                        inst = getattr(objInst,method[3])
                        method[-1]["protocol"] = self.protocol
                        deviceSet = inst(**method[-1])
                    #pouze method
                    else:
                        #print("volam method",method[2])
                        #inst = getattr(objInst,method[2])
                        inst = getattr(objInst,method[2].strip())
                        #print("volam instanci", method[-1])
                        method[-1]["protocol"] = self.protocol
                        deviceSet = inst(**method[-1])
                    
                    if config_method == "hybrid":
                        if deviceSet == None:
                            self.conn.disconnect()
                            return
                        conn.doCommand(deviceSet) 

                else:
                    print("invalid configuration option")

                #resetuj nastaveni pro conn a config
                conn_method = None
                config_method = None
            try:
                self.conn.disconnect()
            except Exeption as e:
                print("nastala vyjimka")
                print(e)
                

                    #sestaveni modulu pro import
#                    module = "device_modules.{}.{}".format(manufactor[0],manufactor[1])
#                    importObj = importlib.import_module(module)
#                    #zavolani tridy
#                    obj = getattr(importObj,method[1])
#                    objInst = obj() #do objektu pridat atribut check, kterej bude kontrovat zda byla proveda kontrolna na pritomnost prikazu nebo ne

                  
                    #zjisteni metody spojeni
#                    conn_method = objInst.method
#                    #pokud se nastavuje submethod
#                    if method[3]:
#                        inst = getattr(objInst,method[3])
#                        deviceSet = inst(**method[-1])
#                    #pouze method
#                    else:
#                        inst = getattr(objInst,method[2])
#                        deviceSet = inst(**method[-1])
#                    
#                    #zavolani propojovaciho modulue a vykonani prikazu
#                    conn = getattr(connect, conn_method)                     
#
#
#                    conn = conn()
#                    conn._connect(host,self.username,self.password)
#                    conn._execCmd(deviceSet)

