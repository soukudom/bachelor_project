#!/usr/bin/env python3
import device_modules.cisco.ciscoC2950 as c
from lxml import etree

class DefaultConnection:
    def __init__(self):
        self.method = "NETCONF"
        self.connection = "auto"

def makeNetconf(commands):
    root = etree.Element("edit-config")
    child = etree.SubElement(root,"target")
    etree.SubElement(child,"running")
    child2 = etree.SubElement(root,"config")
    child21 = etree.SubElement(child2,"cli-config-data")
    for cmd in commands:
        if cmd == "configure terminal" or cmd == "end":
            continue
        child211 = etree.SubElement(child21,"cmd")
        child211.text = cmd
    res = (etree.tostring(root,encoding="utf-8").decode("utf-8"))
    return res

def changeInterfaceName(configuration):
    for no,i in enumerate(configuration):
        if "interface" in i:
            tmp = i.split("/")
            configuration[no] = "interface GigabitEthernet1/0/{}".format(tmp[1])

    return configuration

class agregate(c.agregate):
    def __init__(self):
        self.result = []

    def channel(self,id=""):
        self.result = super().channel(id)
        self.result = makeNetconf(self.result)
        return self.result

    def delete_channel(self,id=""):
        pass


class vlan(c.vlan):
    def __init__(self):
        self.interfaceCount = 28
        self.result = []

    def vlan(self,id="",description="",ip=""):
        self.result = super().vlan(id,description,ip,shutdown)
        self.result = makeNetconf(self.result)
        return self.result 

    def int_vlan(self,id="",description="",ip=""):
        self.result = super().vlan(id,description,ip,shutdown)
        self.result = makeNetconf(self.result)
        return self.result 

    def delete_vlan(self,id):
        self.result = super().delete_vlan(id)
        self.result. = makeNetconf(self.result)
        return selr.result

class interface(c.interface):
    def __init__(self):
      #  super().__init__()
        self.method = "NETCONF"
        self.interfaceCount = 28
        self.result = []

    def int(self,id="",description="",shutdown=""):
        self.result = super().int(id,description,shutdown)
        changeInterfaceName(self.result)
        self.result = makeNetconf(self.result)
        return self.result
    
    def int_vlan(self,id="",mode="",allowed="", access=""):
        self.result = super().int_vlan(id,mode,allowed,access)
        changeInterfaceName(self.result)
        self.result = makeNetconf(self.result)
        return self.result 
    
    def int_agregate(self,id="",channel="",mode="",protocol=""):
        self.result = super().int_agregate(id,channel,mode,protocol)
        changeInterfaceName(self.result)
        self.result = makeNetconf(self.result)
        return self.result 
    
    def delete_int(self, id=""):
        self.result = super().delete_int(id)
        changeInterfaceName(self.result)
        self.result = makeNetconf(self.result)
        return self.result 

class save(c.save):
    def __init__(self):
        self.result = []

    def save_config(self,id="")
        pass
