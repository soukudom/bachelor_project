#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-

import paramiko
import time
import sys
from pysnmp.entity.rfc3413.oneliner import cmdgen
#import subprocess
import pexpect
import socket
from abc import ABCMeta, abstractmethod
from lxml import etree


class Protocol(metaclass=ABCMeta):
    def __init__(self,protocol):
        pass

    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def doCommand(self,command):
        pass

class SSH(Protocol):
    def __init__(self,protocol):# username, password):
        self.username = protocol["username"] 
        self.password = protocol["password"]
        self.ip = protocol["ip"]
        self.result = []
        self.conn = None # Vzdalena console
        self.conn_pre = paramiko.SSHClient() # priprava pro vzdalenou consoli
        self.conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    def connect(self):
        try:
            self.conn_pre.connect(self.ip,username=self.username,password=self.password,look_for_keys=False, allow_agent=False)
        except paramiko.ssh_exception.AuthenticationException:
            raise Exception("Authentication fail")
        self.conn = self.conn_pre.invoke_shell() 
        time.sleep(0.5)
        while self.conn.recv_ready():
            output = self.conn.recv(100)
            print("prihlasil jsem se na", output)
            time.sleep(0.3)
        #print(output)
        return True

    def disconnect(self):
        self.conn_pre.close()
        print("session has been closed")

    def doCommand(self,commands):
        #bude umet cist sekvenci prikazu
        rec = ""
        print(commands)
        for command in commands:
            command = command.strip().strip("'")
            #command = bytes(command+"\n","utf-8") 
            #print("posilam*"+command+"*")
            print("posilam",command)
            #self.conn.send(command+'\n')
            self.conn.send(command+'\n')
            time.sleep(0.7)
            while self.conn.recv_ready():
                #print("ctu smycku")
                ot = self.conn.recv(5000)
                rec += str(ot)
                #self.result.append(str(ot))
                time.sleep(0.3)
            else:
            # asi to bude jenom jednoduse vracet at se to naparsuje jinde:
                #if "%" in self.result:
                    #print("zarizeni vratilo:",self.result, "false")
                #    print("This command '{}' was not proceed due to '{}'".format(command, self.result))
                #else:
                self.result.append(rec)
                print("zarizeni vratilo:",rec)
                rec = ""
                print("zarizeni vratilo:",self.result)
      #  return self.invalidCommands
            
             #   for i in self.result.split("\\n"):
                #for j in i.split("\\n"):
             #       print(i)
        self.result = []
        print("********************************************************")      
            #output = self.remote_conn.recv(5000)

class NETCONF(Protocol):
    def __init__(self,protocol):
        self.ip = protocol["ip"]
        self.username = protocol["username"]
        self.password = protocol["password"]

        self.proc = "" #slouzi pro volani pexpect
        self.ending = "]]>]]>"
        self.conn = None # Vzdalena console
        self.conn_pre = paramiko.SSHClient() # priprava pro vzdalenou consoli
        self.conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.socket2 = ""
        self.ch = ""
        self.trans = ""
        
    
    def connect(self):
        #vytvoreni hello zpravy
        root = etree.Element("hello")
        child = etree.SubElement(root,"capabilities")
        child2 = etree.SubElement(child,"capability")
        child2.text = "urn:ietf:params:netconf:base:1.0"
        helloMessage = etree.tostring(root,xml_declaration=True,encoding= "utf-8").decode("utf-8")+self.ending

        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket2.connect((self.ip,22)) 

        self.trans = paramiko.Transport(self.socket2)
        self.trans.connect(username=self.username,password=self.password)
        
        self.ch = self.trans.open_session()
        self.name = self.ch.set_name("netconf")
        self.ch.invoke_subsystem("netconf")
        self.ch.send(helloMessage)
        time.sleep(0.1)

        #data = self.ch.recv(2048)
        #print(data)
        while self.ch.recv_ready():
            data = self.ch.recv(2048)
            print(data)
        #    data = ch.recv(1024)
        #    print(data)
            
        #ch.close()
        #trans.close()
        #socket2.close()

    def doCommand(self,command):
        root = etree.Element("rpc")
        root.set("message-id","105")
        root.set("xmlns","urn:ietf:params:xml:ns:netconf:base:1.0")
        #child = etree.SubElement(root,"edit-config")
        print(command)
        #spojeni dvou xml
        inside = etree.fromstring(command)
        #it = inside.iter()
        #for elem in it:
        #    tmp = etree.Element(elem.tag)
        #    if elem.text:
        #        tmp.text = elem.text
            #root.append(tmp)
        root.append(inside)
            
        #print(etree.tostring(root,xml_declaration=True,encoding="utf-8",pretty_print=True).decode("utf-8")+self.ending)
        message = etree.tostring(root,xml_declaration=True, encoding ="utf-8").decode("utf-8")+self.ending

        self.ch.send(message)
        time.sleep(0.5)
        #data = self.ch.recv(2048)
        while self.ch.recv_ready():
            data = self.ch.recv(2048)
            print(data)
        #data = self.ch.recv(2048)
        #print(data)


    def disconnect(self):
        print("provadim odhlaseni")
        root = etree.Element("rpc")
        root.set("message-id","105")
        root.set("xmlns","urn:ietf:params:xml:ns:netconf:base:1.0")
        etree.SubElement(root,"close-session")
        closeMessage = etree.tostring(root,xml_declaration=True,encoding= "utf-8").decode("utf-8")+self.ending
        self.ch.send(closeMessage)
        time.sleep(0.1)
        while self.ch.recv_ready():
            data = self.ch.recv(2048)
            print(data)

        self.ch.close()
        self.trans.close()
        self.socket2.close()

        print("odhlaseno")

class SNMP(Protocol):
    def __init__(self,protocol):
        self.ip = protocol["ip"]
        self.community = protocol["community"]
        self.method_type = protocol["method_type"]


    def doCommand(self, mibVariable):
        
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
                cmdgen.UdpTransportTarget((self.ip, 161),timeout=2, retries=0), #objekt co reprezentuje sitovou cestu k zarizeni
                #cmdgen.MibVariable("SNMPv2-MIB", "sysDescr", 0),
                #"1.3.6.1.2.1.1.1.0", musi tu bej i ta ukoncovaci nula
                #"1.3.6.1.2.1.1.5", jinak to nefunguje
                variable, #muze byt sekvence hodnot co chci ziskat
                lookupNames=True, lookupValues=True
            )
        
            if errorStatus:
                #print("errorStatus")
                #print(errorStatus)
                raise Exception(errorStatus)

            elif errorIndication:
                #snmp timeout
                raise Exception(errorIndication)

            else:
                for name, val in varBinds:
                    return val.prettyPrint()
        else:
            print(self.method_type)
            print("operation is not implemented")
            sys.exit(2)

    def connect(self):
        #self.ipAddress = ip
        #self.community = community #nemusi bejt, nastavuju uz v initu

        #overeni spravnych udaju, pokus o ziskani dat
        tmp = self.method_type
        self.method_type="get"
        try:
            res = self.doCommand("sysDescr")  
            return res
        except Exception as e:
            raise 
        finally:
            self.method_type=tmp
    
    def disconnect(self):
        pass
