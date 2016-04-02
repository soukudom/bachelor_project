#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-

#Author: Dominik Soukup, soukudom@fit.cvut.cz

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
    def doCommand(self, command, debug):
        pass


class SSH(Protocol):
    def __init__(self, protocol):  
        self.username = protocol["username"]    #username for authentication
        self.password = protocol["password"]    #password for authentication
        self.ip = protocol["ip"]                #ip address
        self.timeout = protocol["timeout"]      #timeout for connect
        self.result = []                        #result of protocol operation
        self.conn = None                        #remote console connection
        self.conn_pre = paramiko.SSHClient()    #remote console configuration
        self.conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #does not care about known host

    def connect(self):
        try:
            #configure console
            self.conn_pre.connect(self.ip,
                                  username=self.username,
                                  password=self.password,
                                  look_for_keys=False,
                                  allow_agent=False,
                                  timeout=self.timeout)
        except paramiko.ssh_exception.AuthenticationException:
            raise Exception("Authentication failed")
        #invoke command line
        self.conn = self.conn_pre.invoke_shell()
        time.sleep(0.5)
        ##!!! z nakyho duvodu to nefunguje jestu protestovat
        #wait until connection is not established
        #while not self.con.recv_ready():
        #    print("neni ready")
        #    time.sleep(0.3)

        while self.conn.recv_ready():
            output = self.conn.recv(2048)
            time.sleep(0.3)
        return output

    def disconnect(self):
        #closes connection
        self.conn_pre.close()
        return None

    def doCommand(self, commands, debug=""):
        sleep_time = 0 # temp variable for timeout checking

        #commands are list of commands
        rec = "" #temp variable
        if type(commands) != type(list()):
            raise Exception("Bad datatype. List is needed.")
        for command in commands:
            command = command.strip().strip("'")
            self.conn.send(command + '\n')
            if debug:
                print("Sending:",command)
            #waiting until response is not recieved
            while not self.conn.recv_ready():
                time.sleep(0.3)
                sleep_time += 0.3
                if sleep_time > self.timeout:
                    raise Exception("Error: Timeout reached during device configuring.")

            sleep_time = 0
            while self.conn.recv_ready():
                #reads response
                ot = self.conn.recv(
                    5000)
                if debug:
                    print("Receiving:",ot)
                rec += str(ot)
                time.sleep(0.3)
            else:
                self.result.append(rec)
                rec = ""
        return self.result


class NETCONF(Protocol):
    def __init__(self, protocol):
        self.ip = protocol["ip"]                #ip address of device
        self.username = protocol["username"]    #username for authentication
        self.password = protocol["password"]    #password. for authentication
        self.timeout = protocol["timeout"]      #protocol timeout connection
        self.ending = "]]>]]>"                  #netconf ending sequence
        self.conn = None                        #remote console
        self.socket = ""                        #connection socket
        self.ch = ""                            #connection channel
        self.trans = ""                         #connection transport
        self.message_id = 1                     #netconf message id number

    def checkReply(self, data, typ):
        control = {"hello": 0,
                   "capabilities": 0,
                   "capability": 0,
                   "session-id": 0}
        #cut off ending sequence
        data = bytes(data[:-8], "utf-8")
        tree = etree.fromstring(data, etree.XMLParser())
        #goes through all elements and checks if element ok is present (in normal message)
        it = tree.iter()
        for i in it:
            #checking hello message
            if typ == "hello":
                if i.tag in ["hello", "capabilities", "capability",
                             "session-id"]:
                    control[i.tag] += 1
                continue
            #testing normal messages
            pos = i.tag.index("}")
            element = i.tag[pos + 1:]
            if element == "ok":
                return 0
        #final hello checking
        if typ == "hello":
            for val in control.values():
                if val == 0:
                    return 1
                else:
                    return 0
        return 1

    def connect(self):
        print("protocol NETCONF")
        #creates hello message
        root = etree.Element("hello")
        child = etree.SubElement(root, "capabilities")
        child2 = etree.SubElement(child, "capability")
        child2.text = "urn:ietf:params:netconf:base:1.0"
        helloMessage = etree.tostring(
            root,
            xml_declaration=True,
            encoding="utf-8").decode("utf-8") + self.ending
        print("postavil jsem hello message")
        #build socket at port 22
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, 22))

        print("postavil jsem socket")
        #set socket to transport and connect
        self.trans = paramiko.Transport(self.socket)
        self.trans.connect(username=self.username, password=self.password)
        
        #opens session and sets parameters
        self.ch = self.trans.open_session()
        self.ch.settimeout(self.timeout)
        #invoke netconf session
        self.name = self.ch.set_name("netconf")
        self.ch.invoke_subsystem("netconf")
        self.ch.send(helloMessage)
        #waits until any respond is received
       # while not self.ch.recv_ready():
       #     print("cyklus while")
       #     time.sleep(0.1)
       #     sleep_time += 0.1
       #     print("dalsi radek")
       #     if sleep_time > self.timeout:
       #         print("vyjimka")
       #         raise Exception("Error: Timeout reached during device configuring.")
       # print("dostal jsem nejaka data")
        time.sleep(0.5)
        while self.ch.recv_ready():
            data = self.ch.recv(2048).decode("utf-8")
        #check message
        retVal = self.checkReply(data, "hello")
        if retVal == 1:
            raise Exception("Can not connect to device '{}'".format(self.ip),
                            data)
        else:
            return data

    def doCommand(self, command, debug=""):
        sleep_time = 0 # temp variable for timeout checking

        if type(command) != type(str()):
            raise Exception("Bad datatype. Datatype str is needed.")
        #raises message id according to rfc
        self.message_id += 1
        data = ""  #variable which contains received data
        #build message
        root = etree.Element("rpc")
        root.set("message-id", str(self.message_id))
        root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        #concatenates messages
        inside = etree.fromstring(command)
        root.append(inside)

        message = etree.tostring(
            root,
            xml_declaration=True,
            encoding="utf-8").decode("utf-8") + self.ending

        #send created message
        self.ch.send(message)
        #debug message
        if debug:
            print("Sending:",message)
        #waiting for response
        while not self.ch.recv_ready():
            time.sleep(0.1)
            sleep_time += 0.1
            if sleep_time > self.timeout:
                raise Exception("Error: Timeout reached during device configuring.")

        sleep_time = 0
        while self.ch.recv_ready():
            data += self.ch.recv(2048).decode("utf-8")
        #debug message
        if debug:
            print("Receiving:",data)
        retVal = self.checkReply(data, None)

        if retVal == 1:
            print("Error: in netconf message. Check log.")
            raise Exception("NETCONF: Problem with configuring command. {}".format(data))
        else:
            return data


    def disconnect(self):
        #same message building like above
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
        #wainting for response
        while not self.ch.recv_ready():
            time.sleep(0.1)
        while self.ch.recv_ready():
            data = self.ch.recv(2048).decode("utf-8")

        retVal = self.checkReply(data, None)
        if retVal == 1:
            print("Error: during closing netconf session")
            raise Exeption("NETCONF: Problem with closing session", data)
        
        #closes connection session
        self.ch.close()
        self.trans.close()
        self.socket.close()
        return None


class SNMP(Protocol):
    def __init__(self, protocol):
        self.ip = protocol["ip"]                    #ip address of device
        self.community = protocol["community"]      #community string
        self.method_type = protocol["method_type"]  #snmp method type
        self.timeout = protocol["timeout"]          #connection timeout

    def doCommand(self, mibVariables, debug=""):
        #mibVariables are list of snmp commands
        if type(mibVariables) != type(list()):
            raise Exception("Bad datatype. List is needed.")
        for mibVariable in mibVariables:
            #if get method was specified
            if self.method_type == "get":
                #if oid or normal name was inserted
                if "." in mibVariable:
                    variable = mibVariable  # requested data
                else:
                    variable = cmdgen.MibVariable("SNMPv2-MIB", mibVariable, 0)

                cmdGen = cmdgen.CommandGenerator()
                #debug message
                if debug:
                    print("Sending:",variable)
                errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
                    cmdgen.CommunityData(self.community),# security data, for snmp1,2 object which contains community string
                    #object which represents network path to device
                    cmdgen.UdpTransportTarget((self.ip, 161),timeout=self.timeout, retries=0),
                    #cmdgen.MibVariable("SNMPv2-MIB", "sysDescr", 0),
                    #"1.3.6.1.2.1.1.1.0", the ending zero is necessarily
                    #"1.3.6.1.2.1.1.5", otherwise it does not work
                    variable, #could be sequence of values
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
                print("Error: Operation is not implemented")
                raise Exception("Operation '{}' is not implemented".format(self.method_type))

    def connect(self):
        #checkes up username and password by trying get the sysDescr variable
        tmp = self.method_type
        self.method_type = "get"
        try:
            res = self.doCommand(["sysDescr"])
            return res
        except Exception as e:
            #raise
            raise Exception("SNMP can not connect to the device")
        finally:
            self.method_type = tmp
        return ""

    def disconnect(self):
        return None
