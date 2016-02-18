#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-

import paramiko
import time
import sys
from pysnmp.entity.rfc3413.oneliner import cmdgen
import socket
from abc import ABCMeta, abstractmethod
from lxml import etree

#!otestovat pokud zarizeni danej protokol nepodporuje


class Protocol(metaclass=ABCMeta):
    def __init__(self, protocol):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def doCommand(self, command):
        pass


class SSH(Protocol):
    def __init__(self, protocol):  # username, password):
        self.username = protocol["username"]
        self.password = protocol["password"]
        self.ip = protocol["ip"]
        self.timeout = protocol["timeout"]
        self.result = []
        self.conn = None  # Vzdalena console
        self.conn_pre = paramiko.SSHClient()  # priprava pro vzdalenou consoli
        self.conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("pripoj se na ip", self.ip)

    def connect(self):
        try:
            self.conn_pre.connect(self.ip,
                                  username=self.username,
                                  password=self.password,
                                  look_for_keys=False,
                                  allow_agent=False,
                                  timeout=self.timeout)
        except paramiko.ssh_exception.AuthenticationException:
            raise Exception("Authentication failed")
        self.conn = self.conn_pre.invoke_shell()
        time.sleep(0.5)
        while self.conn.recv_ready():
            output = self.conn.recv(2048)
            time.sleep(0.3)
        #print(output)
        return output

    def disconnect(self):
        self.conn_pre.close()

    def doCommand(self, commands):
        #bude umet cist sekvenci prikazu
        rec = ""
      #  print(commands)
        if type(commands) != type(list()):
            raise Exception("Bad datatype. List is needed.")
        for command in commands:
            command = command.strip().strip("'")
            self.conn.send(command + '\n')
            #cekani dokud neprijde nejaka odpoved
            while not self.conn.recv_ready():
                time.sleep(0.3)

            while self.conn.recv_ready():
                #print("ctu smycku")
                ot = self.conn.recv(
                    5000)
                #print(ot)
                rec += str(ot)
                #self.result.append(str(ot))
                time.sleep(0.3)
            else:
                self.result.append(rec)
                rec = ""
        return self.result
        #self.result = []


class NETCONF(Protocol):
    def __init__(self, protocol):
        self.ip = protocol["ip"]
        self.username = protocol["username"]
        self.password = protocol["password"]
        self.timeout = protocol["timeout"]
        self.ending = "]]>]]>"
        self.conn = None  # Vzdalena console
        self.socket = ""
        self.ch = ""
        self.trans = ""
        self.message_id = 1
        print("pripoj se na ip", self.ip)

    def checkReply(self, data, typ):
        control = {"hello": 0,
                   "capabilities": 0,
                   "capability": 0,
                   "session-id": 0}
        #odriznuti ukoncovaci sekvence znaku
        data = bytes(data[:-8], "utf-8")
        tree = etree.fromstring(data, etree.XMLParser())
        #projdu vsechny elementy a kontroluje jestli tam je element ok u norm zpravy
        it = tree.iter()
        for i in it:
            #testovani hello zpravy
            if typ == "hello":
                if i.tag in ["hello", "capabilities", "capability",
                             "session-id"]:
                    control[i.tag] += 1
                continue
            #testovani ostatnich zprav, ty obsahuji i namespace
            pos = i.tag.index("}")
            element = i.tag[pos + 1:]
            if element == "ok":
                return 0
        #kontroluje se spravnou hello zpravy
        if typ == "hello":
            for val in control.values():
                if val == 0:
                    return 1
                else:
                    return 0
        #navratovy kod pokud nastala chyba u netconf zpravy
        return 1

    def connect(self):
        #vytvoreni hello zpravy
        root = etree.Element("hello")
        child = etree.SubElement(root, "capabilities")
        child2 = etree.SubElement(child, "capability")
        child2.text = "urn:ietf:params:netconf:base:1.0"
        helloMessage = etree.tostring(
            root,
            xml_declaration=True,
            encoding="utf-8").decode("utf-8") + self.ending

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, 22))

        self.trans = paramiko.Transport(self.socket)
        self.trans.connect(username=self.username, password=self.password)

        self.ch = self.trans.open_session()
        self.ch.settimeout(self.timeout)
        self.name = self.ch.set_name("netconf")
        self.ch.invoke_subsystem("netconf")
        self.ch.send(helloMessage)
        #time.sleep(0.1)
        #cekani dokud neprijde nejaka odpoved
        while not self.ch.recv_ready():
            time.sleep(0.1)

        while self.ch.recv_ready():
            data = self.ch.recv(2048).decode("utf-8")

        retVal = self.checkReply(data, "hello")
        if retVal == 1:
            #print("loguju netconf message")
            #print(data)
            raise Exception("Can not connect to device '{}'".format(self.ip),
                            data)
        else:
            return data

    def doCommand(self, command):
        if type(command) != type(str()):
            raise Exception("Bad datatype. Datatype str is needed.")
        self.message_id += 1
        data = ""  #obsahujou prijata data ze zarizeni
        root = etree.Element("rpc")
        #root.set("message-id","105")
        root.set("message-id", str(self.message_id))
        root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        #child = etree.SubElement(root,"edit-config")
        #print(command)
        #spojeni dvou xml
        inside = etree.fromstring(command)
        root.append(inside)

        #print(etree.tostring(root,xml_declaration=True,encoding="utf-8",pretty_print=True).decode("utf-8")+self.ending)
        message = etree.tostring(
            root,
            xml_declaration=True,
            encoding="utf-8").decode("utf-8") + self.ending

        self.ch.send(message)
        #cekani dokud neprijde nejaka odpoved
        while not self.ch.recv_ready():
            time.sleep(0.1)
        #time.sleep(0.5)
        #data = self.ch.recv(2048)
        while self.ch.recv_ready():
            data += self.ch.recv(2048).decode("utf-8")

        retVal = self.checkReply(data, None)

        if retVal == 1:
            print("loguju netconf message")
            print(data)
            raise Exception("NETCONF: Problem with configuring command.", data)
        else:
            return data

            #    print(data)

    def disconnect(self):
        self.message_id += 1
        root = etree.Element("rpc")
        root.set("message-id", str(self.message_id))
        root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        etree.SubElement(root, "close-session")
        closeMessage = etree.tostring(
            root,
            xml_declaration=True,
            encoding="utf-8").decode("utf-8") + self.ending
        self.ch.send(closeMessage)
        #time.sleep(0.3)
        #cekani dokud neprijde nejaka odpoved
        while not self.ch.recv_ready():
            time.sleep(0.1)
        while self.ch.recv_ready():
            data = self.ch.recv(2048).decode("utf-8")

        retVal = self.checkReply(data, None)
        if retVal == 1:
            #    print("loguju netconf message")
            #    print(data)
            raise Exeption("NETCONF: Problem with closing session", data)

        self.ch.close()
        self.trans.close()
        self.socket.close()
        return data


class SNMP(Protocol):
    def __init__(self, protocol):
        self.ip = protocol["ip"]
        self.community = protocol["community"]
        self.method_type = protocol["method_type"]
        self.timeout = protocol["timeout"]

    def doCommand(self, mibVariables):
        if type(mibVariables) != type(list()):
            raise Exception("Bad datatype. List is needed.")
        for mibVariable in mibVariables:
            if self.method_type == "get":
                # rozhoduje zda byl zadan oid nebo nazev
                if "." in mibVariable:
                    variable = mibVariable
                else:
                    variable = cmdgen.MibVariable("SNMPv2-MIB", mibVariable, 0)

                cmdGen = cmdgen.CommandGenerator()

                errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
                    cmdgen.CommunityData(self.community),# security data, pro snmp1,2 pouze objekt co drzi community string
                    #cmdgen.UdpTransportTarget((networkName, 161),timeout=2, retries=0), #objekt co reprezentuje sitovou cestu k zarizeni
                    cmdgen.UdpTransportTarget((self.ip, 161),timeout=self.timeout, retries=0), #objekt co reprezentuje sitovou cestu k zarizeni
                    #cmdgen.MibVariable("SNMPv2-MIB", "sysDescr", 0),
                    #"1.3.6.1.2.1.1.1.0", musi tu bej i ta ukoncovaci nula
                    #"1.3.6.1.2.1.1.5", jinak to nefunguje
                    variable, #muze byt sekvence hodnot co chci ziskat
                    lookupNames=True, lookupValues=True
                )

                if errorStatus:
                    print("error status")
                    raise Exception(errorStatus)

                elif errorIndication:
                    #snmp timeout
                    raise Exception(errorIndication)

                else:
                    for name, val in varBinds:
                        return val.prettyPrint()
            else:
                #print(self.method_type)
                print("operation is not implemented")
                raise Exception("Operation '{}' is not implemented".format(self.method_type))

    def connect(self):
        #overeni spravnych udaju, pokus o ziskani dat
        tmp = self.method_type
        self.method_type = "get"
        try:
            res = self.doCommand(["sysDescr"])
            return res
        except Exception as e:
            raise
        finally:
            self.method_type = tmp

    def disconnect(self):
        pass
