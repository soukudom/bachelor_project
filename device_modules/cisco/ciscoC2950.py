#!/usr/bin/env python3
#class info:
#    def __init__(self):
#        self.id = "2950"
    #def info(self):
    #    print("jsem cisco {}".format(self.id))
class DefaultConnection:
    def __init__(self):
        self.method = "SSH"
        self.connection = "auto" #jestli se pripojuje modul nebo se to ma udelat automaticky

class vlan:
    def __init__(self):
        self.method = "SSH"
        self.result = ["configure terminal"]

    def vlan(self,id="",description="",ip="",shutdown=""):
        #slozite id
        if type(id) == type(list()): 
            while id:    
                self.result.append("interface vlan {}".format(id))
                if description:
                    if type(description) == type(list()):
                        self.result.append("description {}".format(description[0]))
                        description = description[1:]
                    else:
                        self.result.append("description {}".format(description))
                if ip: 
                    if type(ip) == type(list()):
                        tmp = ip[0]
                        tmp = tmp.split("/")
                        if str(tmp[1]) == str(24):
                            tmp[1] = "255.255.255.0"
                        self.result.append("ip address {} {}".format(tmp[0],tmp[1]))
                        ip = ip[1:]
                    else:
                        ip = ip.split("/")
                        if str(ip[1]) == str(24):
                            ip[1] = "255.255.255.0"
                        self.result.append("ip address {} {}".format(ip[0], ip[1]))
                id = id[1:]
        else:
        #jednoduche id
            if id:
                self.result.append("interface vlan {}".format(id))
            if description:
                self.result.append("description {}".format(description))
            if ip:
                ip = ip.split("/")
                if str(ip[1]) == str(24):
                    ip[1] = "255.255.255.0"
                self.result.append("ip address {} {}".format(ip[0], ip[1]))
            
    
        return self.result 

class interface:
    def __init__(self):
        self.method = "SSH"
        self.result = ["configure terminal"]
        self.interfaceCount = 24 #muzu si dovolit, protoze je to psany pro konkretni model a vim kolim ma rozhrani

    def int(self, id="", description = "", shutdown="",):
        #pokud je zadany id range
        if type(id) == type(list()):
            while id:
                self.result.append("interface FastEthernet 0/{}".format(id[0])) 
                if description:
                    if type(description) == type(list()):
                        self.result.append("description {}".format(description[0]))
                        description = description[1:]
                    else:
                        self.result.append("description {}".format(description))
                if shutdown:
                    self.result.append("shutdown")
                else:
                    self.result.append("no shutdown")
                id = id[1:]
        #pouze jednoduche id
        else: 
            if id:
                self.result.append("interface FastEthernet 0/{}".format(id)) 
            if description:
                self.result.append("description {}".format(description))
            #shutdown vraci yes nebo no
            if shutdown:
                self.result.append("shutdown")
            else:
                self.result.append("no shutdown")
        self.result.append("end")
        print("int je",self.result)
        return self.result

    
    def int_vlan(self,id="",mode="",allowed="", access=""):
        #allowed
        print("int_vlan")
        if type(allowed) == type(list()):
            print("slozity allowed")
            tmp = ""
            for i in allowed:
                tmp += str(i) + ","
            allowed = tmp[:-1]
                
        #slozite id
        if type(id) == type(list()):
            while id:
                print("allowed je", allowed)
                self.result.append("interface FastEthernet 0/{}".format(id[0]))
                if mode:
                    print("pridavam mode")
                    self.result.append("switchport mode {}".format(mode))                        
                if allowed:
                    print("pridavam allowed")
                    self.result.append("switchport trunk allowed vlan {}".format(allowed))
                if access:
                    print("pridavam access")
                    self.resutl.append("switchport access vlan {}".format(access))
                id = id[1:]
        else:
        #jednoduche id
            if id:
                self.result.append("interface FastEthernet 0/{}".format(id))
            if mode:
                self.result.append("switchport mode {}".format(mode))
            if allowed: 
                self.result.append("switchport trunk allowed vlan {}".format(allowed))
            if access:
                self.result.append("switchport access vlan {}".format(access))

        self.result.append("end")
        print("int_vlan je", self.result)
        return self.result
    
    def int_agregate(self,id="",protocol="",channel="",mode=""):
        if type(id) == type(list):
            while id:
                pass
        if id:
            self.result.append("interface FastEthernet 0/{}".format(id))
        if channel and mode:
            mode = "on"
            self.result.append("channel-group {} mode {}".format(channel,mode))
        if protocol:
            self.result.append("channel-protocol {}".format(protocol))

        return self.result
            
        

    def default(self, id="", shutdown="", description=""):
        #result = ["configure terminal"]
        if id:
            idSet = []
            for i in range(self.interfaceCount+1):
                if i in id:
                    continue
                else:
                    self.int(i,description,shutdown)
            return self.result
                    
    
    def default_vlan(self,id="", mode="", access="", allowed=""):
        if id:
            idSet = []
            for i in range(self.interfaceCount+1):
                if i in id:
                    continue
                else:
                    self.int_vlan(i,mode,allowed,access)
            return self.result

    #def mac(self, id="", description = "", shutdown=""):
    #    #!!!id = najdi cislo rozhrani s mac addressou
    #    self.int(id,description,shutdown)
    
    #def mac_vlan(self, id="", mode="", allowed="", access=""):
    #    #!!!id = najdi cislo rozhrani s mac adresoun
    #    self.int_vlan(self, id="", mode="", allowed="", access="")

    #def mac_agregate(self,id="",protocol="",channel="", mode=""):
    #    #!!!id = najdi cislo rozhrani s mac adresoun
    #    self.int_agregate(id,protocol,channel,mode)
