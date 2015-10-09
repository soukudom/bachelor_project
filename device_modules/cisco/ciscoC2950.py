#!/usr/bin/env python3

class vlan:
    def __init__(self):
        self.method = "ssh"

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

    def int(self, id="", description = "", shutdown=""):
        pass

    def int_vlan(self,mode="",allowed=""):
        pass
    
    def int_agregate(self,protocol="",channel="",mode=""):
        pass

    def default(self, id="", shutdown="", description=""):
        pass
    
    def default_vlan(self,id="", mode="", access=""):
        pass

    def mac(self, address=""):
        pass
    
    def mac_vlan(self, mode="", allowed=""):
        pass

    def mac_agregate(self,protocol="",channel="", mode=""):
        pass
