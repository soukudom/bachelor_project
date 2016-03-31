#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: Dominik Soukup: soukudom@fit.cvut.cz

import modules.connect as connect


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
        self.method = "SSH"
        self.connection = "auto"  #jestli se pripojuje modul nebo se to ma udelat automaticky


class vlan:
    def __init__(self):
        self.method = "SSH"
        self.connection = "auto"
        self.result = ["configure terminal"]

    def vlan(self, id="", description="", ip="", shutdown="",protocol=""):
        #slozite id
        if type(id) == type(list()):
            while id:
                self.result.append("interface vlan {}".format(id))
                if description:
                    if type(description) == type(list()):
                        self.result.append("description {}".format(description[
                            0]))
                        description = description[1:]
                    else:
                        self.result.append("description {}".format(
                            description))
                if ip:
                    if type(ip) == type(list()):
                        print("volam slozitou ip. device modul")
                        #tmp = ip[0]
                        #tmp = tmp.split("/")
                        #    
                        #if str(tmp[1]) == str(24):
                        #    tmp[1] = "255.255.255.0"
                        #self.result.append("ip address {} {}".format(tmp[0],
                        #                                             tmp[1]))
                        #ip = ip[1:]
                    else:
                        ip = ip.split("/")
                        ip[1] = transformMask(ip[1])
                        if ip[1] == None:
                           return None 
                        #if str(ip[1]) == str(24):
                        #    ip[1] = "255.255.255.0"
                        self.result.append("ip address {} {}".format(ip[0], ip[
                            1]))
                id = id[1:]
        else:
            #jednoduche id
            if id:
                self.result.append("interface vlan {}".format(id))
            if description:
                self.result.append("description {}".format(description))
            if ip:
                ip = ip.split("/")
                ip[1] = transformMask(ip[1])
                if ip[1] == None:
                    return None
                self.result.append("ip address {} {}".format(ip[0], ip[1]))

        return self.result


class interface:
    def __init__(self):
        self.method = "SSH"
        self.result = ["configure terminal"]
        self.interfaceCount = 24  #muzu si dovolit, protoze je to psany pro konkretni model a vim kolim ma rozhrani
        #self.connection = "hybrid"

    def int(self, id="", description="", shutdown=""):
        #pokud je zadany id range
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
        return self.result

    def delete_int(self, id=""):
        #print("delete_int")
        if type(id) == type(list()):
            while id:
                self.result.append("interface FastEthernet 0/{}".format(id[0]))
                self.result.append("no description")
                self.result.append("shutdown")
                self.result.append("no switchport mode")
                self.result.append("no switchport trunk allowed vlan")
                id = id[1:]
        else:
            if id:
                self.result.append("interface FastEthernet 0/{}".format(id))
                self.result.append("no description")
                self.result.append("shutdown")
                self.result.append("no switchport mode")
                self.result.append("no switchport trunk allowed vlan")
        self.result.append("end")
        return self.result

    def int_vlan(self, id="", mode="", allowed="", access=""):
        #print("metoda int_vlan", id)
        #allowed
        if type(allowed) == type(list()):
            print("slozity allowed")
            tmp = ""
            for i in allowed:
                tmp += str(i) + ","
            allowed = tmp[:-1]

            #slozite id
        if type(id) == type(list()):
            while id:
                #print("allowed je", allowed)
                self.result.append("interface FastEthernet 0/{}".format(id[0]))
                if mode:
                    #print("pridavam mode")
                    self.result.append("switchport mode {}".format(mode))
                if allowed:
                    #print("pridavam allowed")
                    self.result.append(
                        "switchport trunk allowed vlan {}".format(allowed))
                if access:
                    #print("pridavam access")
                    self.result.append("switchport access vlan {}".format(
                        access))
                id = id[1:]
        else:
            #jednoduche id
            if id:
                self.result.append("interface FastEthernet 0/{}".format(id))
            if mode:
                self.result.append("switchport mode {}".format(mode))
            if allowed:
                self.result.append("switchport trunk allowed vlan {}".format(
                    allowed))
            if access:
                self.result.append("switchport access vlan {}".format(access))

        self.result.append("end")
        return self.result

    def int_agregate(self,
                     id="",
                     channel="",
                     mode="",
                     protocol=""):
        print("metoda agregate", id, channel, mode , protocol)
        if type(id) == type(list()):
            while id:
                print("slozity id")
                self.result.append("interface FastEthernet 0/{}".format(id[0]))
                if channel and mode:
                    self.result.append("channel-group {} mode {}".format(channel,mode))
                if protocol:
                    self.result.append("channel-protocol {}".format(protocol))
                id = id[1:]
            
        else:
            print("jednoduchy id")
            if id:
                self.result.append("interface FastEthernet 0/{}".format(id))
            if channel and mode:
                mode = "on"
                self.result.append("channel-group {} mode {}".format(channel,
                                                                 mode))
            if protocol:
                self.result.append("channel-protocol {}".format(protocol))

        self.result.append("end")
        return self.result

        #def default(self, id="", shutdown="", description=""):
        #    #result = ["configure terminal"]
        #    if id:
        #        idSet = []
        #        for i in range(self.interfaceCount+1):
        #            if i in id:
        #                continue
        #            else:
        #                self.int(i,description,shutdown)
        #        return self.result

        #def default_vlan(self,id="", mode="", access="", allowed=""):
        #    if id:
        #        idSet = []
        #        for i in range(self.interfaceCount+1):
        #            if i in id:
        #                continue
        #            else:
        #                self.int_vlan(i,mode,allowed,access)
        #        return self.result

        #def mac(self, id="", description = "", shutdown=""):
        #    #!!!id = najdi cislo rozhrani s mac addressou
        #    self.int(id,description,shutdown)

        #def mac_vlan(self, id="", mode="", allowed="", access=""):
        #    #!!!id = najdi cislo rozhrani s mac adresoun
        #    self.int_vlan(self, id="", mode="", allowed="", access="")

        #def mac_agregate(self,id="",protocol="",channel="", mode=""):
        #    #!!!id = najdi cislo rozhrani s mac adresoun
        #    self.int_agregate(id,protocol,channel,mode)
