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
        self.method = "CLI"
        self.connection = "auto"

class agregate:
    def __init__(self):
        self.result = ["system-view"]
    def channel(self, id=""):
        if type(id) == type(list()):
            while id: 
                self.result.append("link-aggregation group {} mode static".format(id[0]))
                id = id[1:]
        else:
            self.result.append("link-aggregation group {} mode static".format(id))
        self.result.append("return")
        return self.result

    def delete_channel(self,id=""):
        if type(id) == type(list()):
            while id: 
                self.result.append("undo link-aggregation group {}".format(id[0]))
                id = id[1:]
        else:
            self.result.append("undo link-aggregation group {}".format(id))
        self.result.append("return")
        return self.result

        

class vlan:
    def __init__(self):
        self.result = ["system-view"]

    def vlan(self,id="",name=""):
        if type(id) == type(list()):
            while id: 
                self.result.append("vlan {}".format(id[0]))
                if name:
                    if type(name) == type(list()):
                        self.result.append("name {}".format(name[0]))
                        name = name[1:]
                    else:
                        self.result.append("name {}".format(name))
                id = id[1:]
        else:
            self.result.append("vlan {}".format(id))
            if name:
                self.result.append("name {}".format(name))
        self.result.append("return")
        return self.result
            

    def int_vlan(self, id="",description="",ip=""):
        if type(id) == type(list()):
            while id:
                self.result.append("interface Vlan-interface {}".format(id[0]))
                if description:
                    if type(description) == type(list()):
                        self.result.append("description {}".format(description[0]))
                        description[1:]
                    else:
                        self.result.append("description {}".format(description))
                if ip and type(ip) == type(str()):
                    ip = ip.split("/")
                    ip[1] = transformMask(ip[1])
                    if ip[1] == None:
                        return None
                    self.result.append("ip address {} {}".format(ip[0],ip[1]))
                id = id[1:]
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
                self.result.append("ip address {} {}".format(ip[0],ip[1]))
        self.result.append("return")
        return self.result

    def delete_vlan(self,id):
        if type(id) == type(list()):
            while id:
                self.result.append("undo vlan {}".format(id[0]))
                id = id[1:]
        else:
            self.result.append("undo vlan {}".format(id))
        self.result.append("return")
        return self.result

class interface:
    def __init__(self):
        self.result = ["system-view"]

    def int(self, id="", description="", shutdown=""):
        if type(id) == type(list()):
            while id:
                self.result.append("interface Ethernet1/0/{}".format(id[0]))
                if description:
                    if type(description) == type(list()):
                        self.result.append("description {}".format(description[0]))
                        description = description[1:]
                    else:
                        self.result.append("description {}".format(description))
                if shutdown:
                    self.result.append("shutdown")
                else:
                    self.result.append("undo shutdown")
                    
    
                id = id[1:]
        else:
            if id:
                self.result.append("interface Ethernet1/0/{}".format(id))
            if description:
                self.result.append("description {}".format(description[0]))
            if shutdown:
                self.result.append("shutdown")
            else:
                self.result.append("undo shutdown")
        self.result.append("return")
        return self.result

    def delete_int(self,id=""):
        if type(id) == type(list()):
            while id:
                self.result.append("interface Ethernet1/0/{}".format(id[0]))
                self.result.append("undo description")
                self.result.append("undo lacp enable")
                self.result.append("undo port link-type") 
                self.result.append("undo port link-aggregation group")
                self.result.append("shutdown")
                id = id[1:]
        else:
            if id:
                self.result.append("interface Ethernet1/0/{}".format(id))
                self.result.append("undo description")
                self.result.append("undo lacp enable")
                self.result.append("undo port link-type")
                self.result.append("undo port link-aggregation group")
                self.result.append("shutdown")
        self.result.append("return")
        return self.result

    def int_vlan(self,id="", mode="", allowed="", access=""):
        if type(allowed) == type(list()):
            tmp = ""
            for i in allowed:
                tmp += str(i) + " " 
            allowed = tmp[:-1]
        if type(id) == type(list()):
            while id:
                self.result.append("interface Ethernet1/0/{}".format(id[0]))
                if mode:
                    self.result.append("port link-type {}".format(mode))
                if allowed:
                    self.result.append("port trunk permit vlan {}".format(allowed))
                if access:
                    self.result.append("port access vlan {}".format(access))
                id = id[1:]
        else:
            if id:
                self.result.append("interface Ethernet1/0/{}".format(id))
            if mode:
                self.result.append("port link-type {}".format(mode))
            if allowed:
                self.result.append("port trunk permit vlan {}".format(allowed))
            if access:
                self.result.append("port access vlan {}".format(access))

        self.result.append("return")
        return self.result


    def int_agregate(self,id="",channel="",mode="",protocol=""):
        if type(id) == type(list()):
            while id: 
                self.result.append("interface Ethernet1/0/{}".format(id[0]))
                if channel:
                    self.result.append("port link-aggregation group {}".format(channel))
                if protocol:
                    self.result.append("{} enable".format(protocol))
                id = id[1:]
     
        else:
            if id: 
                self.result.append("interface Ethernet1/0/{}".format(id))
            if channel:
                self.result.append("port link-aggregation group {}".format(channel))
            if protocol:
                self.result.append("{} enable".format(protocol))

        self.result.append("return")
        return self.result

class save:
    def __init__(self):
        self.result = ["save"]

    def save_config(self,id=""):
        self.result.append("y")
        self.result.append("\n")
        return self.result
