#!/usr/bin/env python3
#class info:
#    def __init__(self):
#        self.id = "2950"
    #def info(self):
    #    print("jsem cisco {}".format(self.id))
class DefaultConnection:
    def __init__(self):
        self.method = "ssh"

class vlan:
    def __init__(self):
        self.method = "ssh"
    #!!! udelat nastavovani pro range id jako v int
    def vlan(self,id="",description="",ip="",shutdown=""):
        result = ["configure terminal"]
        if id:
            result.append("interface vlan {}".format(id))
        if description:
            result.append("description {}".format(description))
        if ip:
            ip = ip.split("/")
            if str(ip[1]) == str(24):
                ip[1] = "255.255.255.0"
            result.append("ip address {} {}".format(ip[0], ip[1]))
    
        return result 

class interface:
    def __init__(self):
        self.method = "ssh"
        self.result = ["configure terminal"]
        self.interfaceCount = 24 #muzu si dovolit, protoze je to psany pro konkretni model a vim kolim ma rozhrani
    def int(self, id="", description = "", shutdown="",):
        print("jsem v metode int")
        #result = ["configure terminal"]
        #pokud je zadany id range
        if type(id) == type(list()):
            print("slozite id")
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
            print("jednoduche id")
            if id:
                self.result.append("interface FastEthernet 0/{}".format(id)) 
            if description:
                self.result.append("description {}".format(description))
            #if shutdown != "":
            #shutdown vraci yes nebo no
            if shutdown:
                self.result.append("shutdown")
            else:
                self.result.append("no shutdown")
        self.result.append("end")
        print("result je",self.result)
        return self.result

    
    def int_vlan(self,id="",mode="",allowed="", access=""):
        #result = ["configure terminal"]
        if id:
            self.result.append("interface FastEthernet 0/{}".format(id))
        if mode:
            self.result.append("switchport mode access")
        if allowed:
            self.result.append("switchport trunk allowed vlan {}".fromat(allowed))
        if access:
            self.result.append("switchport access vlan {}".format(access))

        return self.result
    
    def int_agregate(self,id="",protocol="",channel="",mode=""):
        #result = ["configure terminal"] 
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

    def mac(self, id="", description = "", shutdown=""):
        #!!!id = najdi cislo rozhrani s mac addressou
        self.int(id,description,shutdown)
    
    def mac_vlan(self, id="", mode="", allowed="", access=""):
        #!!!id = najdi cislo rozhrani s mac adresoun
        self.int_vlan(self, id="", mode="", allowed="", access="")

    def mac_agregate(self,id="",protocol="",channel="", mode=""):
        #!!!id = najdi cislo rozhrani s mac adresoun
        self.int_agregate(id,protocol,channel,mode)
