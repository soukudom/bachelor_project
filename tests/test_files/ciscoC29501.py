#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################
# Author: Dominik Soukup, soukudom@fit.cvut.cz #
################################################

import modules.connect as connect

#changes connection manner of configuring, from auto to others
def connect2device(conn_method, protocol):
    conn = getattr(connect, conn_method)
    conn = conn(protocol)
    try:
        conn.connect()
        return conn
    except Exeption as e:
        return None


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

class vlan:
    def __init__(self):
        self.method = "CLI"
        self.connection = "manual"
        self.result = ["configure terminal"]

    def vlan(self,id="",name="",protocol=""):
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
        self.result.append("end")
        conn = connect2device(self.method,protocol)
        conn.doCommand(self.result,"d")
        return self.result

class interface:
    def __init__(self):
        self.method = "CLI"
        self.connection = "hybrid"
        self.result = ["configure terminal"]
        self.interfaceCount = 24

    def int(self, id="", description="", shutdown="",protocol=""):
        if type(id) == type(list()):
            while id:
                self.result.append("interface FastEthernet 0/{}".format(id[0]))
                if description:
                    if type(description) == type(list()):
                        self.result.append("description {}".format(description[
                            0]))
                        description = description[1:]
                    else:
                        self.result.append("description {}".format(
                            description))
                if shutdown:
                    self.result.append("shutdown")
                else:
                    self.result.append("no shutdown")
                id = id[1:]
        else:
            if id:
                self.result.append("interface FastEthernet 0/{}".format(id))
            if description:
                self.result.append("description {}".format(description))
            if shutdown:
                self.result.append("shutdown")
            else:
                self.result.append("no shutdown")
        self.result.append("end")
        return self.result

