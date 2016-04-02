#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: Dominik Soukup

import modules.connect as connect

def transformMask(mask):
    try:
        mask = int(mask)
    except TypeError:
        return None
    octet_mask = [0,0,0,0]
    pos = -1
    if mask == 0:
        return "0.0.0.0"
    for bit in range(0,mask):
        if bit%8 == 0:
            base = 256 
            pos += 1
        base = int(base/2)
        octet_mask[pos] += base
    return ".".join(str(octet) for octet in octet_mask)



class DefaultConnection:
    def __init__(self):
        self.method = "SSH"
        self.connection = "auto"

class vlan:
    def __init__(self):
        self.result = ["system-view"]

    def vlan(self, id="",description="",ip=""):
        if type(id) == type(list()):
            while id:
                self.result.append("interface Vlan-interface {}".format(id[0]))
                if description:
                    if type(description) == type(list()):
                        self.result.append("description {}".format(description[0]))
                        description[1:]
                    else:
                        self.result.append("description {}".format(description))
                if ip:
                    ip = ip.split("/")
                    ip[1] = transformMask(ip[1])
                    if ip[1] == None:
                        return None
                    self.result.append("ip address {} {}".format(ip[0],ip[1]))
                id[1:]
        else:
            if id:
                self.result.append("interface Vlan-interface {}".format(id))
            if description:
                self.result.append("description {}".format(description))
            if ip:
                ip = ip.split("/")
                ip[1] = transformMask(ip[1])
                if ip[1] == None:
                    return None

    def delete_vlan(self,id):
        if type(id) == type(list()):
            while id:
                self.result.append("undo vlan {}".format(id[0]))
                id = id[1:]
        else:
            self.result.append("undo vlan {}".format(id))

class interface:
    def __init__(self):
        self.result = ["system-view"]

    def int(self, id="", description="", shutdown=""):
        if type(id) == type(list()):
            while id:
    
                id[1:]
        else:
            pass

    def delete_int(self,id=""):
        pass

    def int_vlan(self,id="", mode="", allowed="", access=""):
        pass

    def int_agregate(self,id="",channel="",mode="",protocol=""):
        pass
