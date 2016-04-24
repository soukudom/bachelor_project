#!/usr/bin/env python3
import device_modules.cisco.ciscoC2950 as c
from lxml import etree

#protocol name wich is not exists
class DefaultConnection:
    def __init__(self):
        self.method = "XXX"
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
            if "default" in tmp[0]:
                configuration[no] = "default interface GigabitEthernet1/0/{}".format(tmp[1])
            else:
                configuration[no] = "interface GigabitEthernet1/0/{}".format(tmp[1])

    return configuration

class agregate(c.agregate):
    def __init__(self):
        self.result = []

    def channel(self,id=""):
        self.result = super().channel(id)
        self.result = makeNetconf(self.result)
        return [self.result]

    def delete_channel(self,id=""):
        self.result = super().delete_channel(id)
        self.result = makeNetconf(self.result)
        return [self.result]

