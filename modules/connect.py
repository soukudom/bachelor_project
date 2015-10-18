#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-

import paramiko
import time
import sys
from pysnmp.entity.rfc3413.oneliner import cmdgen
#import subprocess
import pexpect
import socket


class ssh():
    def __init__(self):# username, password):
        self.result = ""
        self.conn = None # Vzdalena console
        self.conn_pre = paramiko.SSHClient() # priprava pro vzdalenou consoli
        self.conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    def _connect(self,ip,username,password):
        try:
            self.conn_pre.connect(ip,username=username,password=password,look_for_keys=False, allow_agent=False)
        except paramiko.ssh_exception.AuthenticationException:
            print("chyba autentizace")
            return False
        self.conn = self.conn_pre.invoke_shell() 
        time.sleep(0.5)
        #!! mozna si pohlidat smyckou jestli je vstup prazdnej
        while self.conn.recv_ready():
            output = self.conn.recv(100)
            print("prihlasil jsem se na", output)
            time.sleep(0.3)
        #print(output)
        return True

    def _execCmd(self,commands):
        #bude umet cist sekvenci prikazu
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
                self.result = str(ot)
                time.sleep(0.3)
            else:
            # asi to bude jenom jednoduse vracet at se to naparsuje jinde:
                if "%" in self.result:
                    #print("zarizeni vratilo:",self.result, "false")
                    print("This command '{}' was not proceed due to '{}'".format(command, self.result))
                else:
                    print("zarizeni vratilo:",self.result)
      #  return self.invalidCommands
            
             #   for i in self.result.split("\\n"):
                #for j in i.split("\\n"):
             #       print(i)
        print("********************************************************")      
            #output = self.remote_conn.recv(5000)

class netconf():
    def __init__(self):
        self.proc = "" #slouzi pro volani pexpect

        self.conn = None # Vzdalena console
        self.conn_pre = paramiko.SSHClient() # priprava pro vzdalenou consoli
        self.conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.socket2 = ""
        self.ch = ""
        self.trans = ""
        
    
    def _connect2(self,ip,username,password, helloMessage):
        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket2.connect((ip,22)) 

        self.trans = paramiko.Transport(self.socket2)
        self.trans.connect(username=username,password=password)
        
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

    def _execCmd2(self, command):
        self.ch.send(command)
        time.sleep(0.1)
        #data = self.ch.recv(2048)
        while self.ch.recv_ready():
            data = self.ch.recv(2048)
            print(data)
        #data = self.ch.recv(2048)
        #print(data)

        self.ch.close()
        self.trans.close()
        self.socket2.close()

    def _connect(self, ip, username, password, helloMessage):
        self.proc = pexpect.spawn("ssh {}@{} -s netconf".format(username,ip))
        self.proc.expect("Password:")
        self.proc.sendline(password) 
        self.proc.expect(".*\]\]>\]\]>")
        print(self.proc.after.decode("utf-8"))
        self.proc.sendline(helloMessage)
        #self.proc.sendline('<?xml version="1.0" encoding="UTF-8"?><hello><capabilities><capability>urn:ietf:params:netconf:base:1.0</capability><capability>urn:ietf:params:netconf:capability:writeable-running:1.0</capability><capability>urn:ietf:params:netconf:capability:startup:1.0</capability><capability>urn:ietf:params:netconf:capability:url:1.0</capability><capability>urn:cisco:params:netconf:capability:pi-data-model:1.0</capability><capability>urn:cisco:params:netconf:capability:notification:1.0</capability></capabilities></hello>]]>]]>') 
        time.sleep(0.1)

    def _execCmd(self, commands):
        self.proc.sendline(commands)
        time.sleep(0.1)
        self.proc.expect(".*\]\]>\]\]>")
        print(self.proc.after.decode("utf-8"))

class snmp():
    def __init(self):
        pass

    def _snmpGet(self,networkName, community, mibVariable):
        # rozhoduje zda byl zadan oid nebo nazev
        if "." in mibVariable:
            variable = mibVariable
        else:
            variable = cmdgen.MibVariable("SNMPv2-MIB", mibVariable, 0)

        cmdGen = cmdgen.CommandGenerator()

        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            cmdgen.CommunityData(community),# security data, pro snmp1,2 pouze objekt co drzi community string
            cmdgen.UdpTransportTarget((networkName, 161),timeout=2, retries=0), #objekt co reprezentuje sitovou cestu k zarizeni
            #cmdgen.MibVariable("SNMPv2-MIB", "sysDescr", 0),
            #"1.3.6.1.2.1.1.1.0", musi tu bej i ta ukoncovaci nula
            #"1.3.6.1.2.1.1.5", jinak to nefunguje
            variable, #muze byt sekvence hodnot co chci ziskat
            lookupNames=True, lookupValues=True
        )
        
        if errorStatus:
            print("errorStatus")
            print(errorStatus)

        elif errorIndication:
            #snmp timeout
            print("errorIndication")
            print(errorIndication)

        else:
            for name, val in varBinds:
                return val.prettyPrint()
