#!/usr/bin/env python3

class DefaultConnection:
    def __init__:
        self.method = "NETCONF"
        self.connection = "auto"


class vlan:
    def __init__(self):
        self.method = "netconf"

    def vlan(self,id="",description="",ip="",shutdown=""):
        self.result = ""
        return self.result 

class interface:
    def __init__(self):
        self.method = "netconf"
    
    def int(self, id="", description = "", shutdown="",):
        self.result = ""
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
        print("result je",self.result)
        #return self.result 

    
    def int_vlan(self,id="",mode="",allowed="", access=""):
        self.result = ""
        return self.result 
    
    def int_agregate(self,id="",protocol="",channel="",mode=""):
        self.result = ""
        return self.result 

    def default(self, id="", shutdown="", description=""):
        self.result = ""
        return self.result 
    
    def default_vlan(self,id="", mode="", access="", allowed=""):
        self.result = ""
        return self.result 

    def mac(self, id="", description = "", shutdown=""):
        self.result = ""
        return self.result 
    
    def mac_vlan(self, id="", mode="", allowed="", access=""):
        self.result = ""
        return self.result 

    def mac_agregate(self,id="",protocol="",channel="", mode=""):
        self.result = ""
        return self.result 
