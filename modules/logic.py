#!/usr/vin/env python3

import getpass
import sys
import os
import modules.factory as factory

class _orchestrate:    
    def __init__(self, deviceFile, configFile, settingsFile ):

        self.deviceFile = deviceFile
        self.configFile = configFile
        self.settingsFile = settingsFile
        self.factory = factory.Factory()

        globalSettings = self.factory.getSettingsProcessing(self.settingsFile) #iparseSettings(self.settingsFile)
        globalSettings.parse("")
        if not self.configFile: 
            try:
                self.configFile = globalSetting.settingsData[config_file]
            except KeyError as e:
                print("Config file has not been inserted")
                sys.exit(1)

        if not self.deviceFile:
            try:
                self.deviceFile = globalSetting.settingsData[device_file]
            except KeyError as e:
                print("Config file has not been inserted")
                sys.exit(1)
        
        instance = "obj" # instace tridy v pomocnym volani
        returned = "res" # navratova hodnota
        self.username = input("Type your username:") #username pro prihlaseni na zarizeni
        self.password = getpass.getpass("Type your password:") #password pro prihlaseni
        
        
        device = self.factory.getDeviceProcessing(self.deviceFile) #parseDevice(self.deviceFile)
        config = self.factory.getConfigProcessing(self.configFile) #parseConfig(configFile)
        methods = config.parse("")
        for method in methods:
            print("metoda k nastaveni:",method)
            hosts = device.parse(method[0]) # zjisti zarizeni, ktere se budou nastavovat         
            print("zarizeni k nastaveni",hosts)
            for vendor in hosts: # zjisti nazev zarizeni, ktery je potrebny pro dynamickou praci
                print("vendor je ", vendor)
                for host in hosts[vendor]:
                    manufactor = device._getManufactor(host,globalSettings.settingsData["community_string"])
                    print("vyrobce:",manufactor)
                    continue
## >>>>>>>>>>>>>>>>>
                    exit(1)                 
                    #sestaveni modulu pro import
                    module = "device_modules.{}.{}".format(manufactor[0],manufactor[1])
                    importObj = importlib.import_module(module)
                    #zavolani tridy
                    obj = getattr(importObj,method[1])
                    objInst = obj() #do objektu pridat atribut check, kterej bude kontrovat zda byla proveda kontrolna na pritomnost prikazu nebo ne

                  
                    #zjisteni metody spojeni
                    conn_method = objInst.method
                    #pokud se nastavuje submethod
                    if method[3]:
                        inst = getattr(objInst,method[3])
                        deviceSet = inst(**method[-1])
                    #pouze method
                    else:
                        inst = getattr(objInst,method[2])
                        deviceSet = inst(**method[-1])
                    
                    #zavolani propojovaciho modulue a vykonani prikazu
                    conn = getattr(connect, conn_method)                     


                    conn = conn()
                    conn._connect(host,self.username,self.password)
                    conn._execCmd(deviceSet)



#                    #dynamicke vytvoreni skriptu pro nastaveni
#                    try:
#                        with open(manufactor[1]+".py", encoding="utf-8", mode="w") as f:
#                            print("#!/usr/bin/env python3", file=f)
#                            print("import device_modules.{}.{} as {}".format(manufactor[0],manufactor[1],manufactor[1]), file=f) 
#                            
#                            #vytvoreni objektu tridy
#                            print("{} = {}.{}()".format(instance,manufactor[1],method[1]),file=f)
#                            #pokud je definovana submethod
#                            if method[3]:
#                                print("{} = {}.{}(**{})".format(returned,instacen,method[3],method[-1]),file=f)
#                            #pokud je definovano prouze method
#                            else:
#                                print("{} = {}.{}(**{})".format(returned,instance,method[2],method[-1]),file=f)
#                            #vrati vysledek operace
#                            print("print({},{}.method)".format(returned,instance),file=f)
#                            
#                    except Exception as e:
#                        print(e)
#                    #zavolani pomocneho souboru    
#                    p = subprocess.Popen(["python3", manufactor[1]+".py"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
#                    output, error = p.communicate()
#                    
#                    #print("ot:", output)
#                    deviceSet = output.decode("utf-8").rsplit(" ",1)
#                    deviceSet[0] = deviceSet[0].strip("][").split(",")
#                    if deviceSet[1].strip() == "ssh":
#                        conn = connect.ssh()
#                        conn._connect(host,self.username, self.password)
#                        conn._execCmd(deviceSet[0])
                                

        #name =  parseDevice(self.deviceFile)._getManufactor("10.10.110.232") 
        #print(name)

        #par = parseSettings(settingsFile)
        #par._parse()
        #print(par.network,par.networkMask,par.community,par.deviceFile,par.configFile)
        
        #obj = ssh("10.10.110.230",self.username,self.password)    
        #obj._execCmd("show run")

    # vhodne zde paralelizovat / advance
