#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-

import paramiko
import time
import sys
from pysnmp.entity.rfc3413.oneliner import cmdgen


class ssh():
    def __init__(self,ip, username, password):
        #!!! self.result = None # mozna pro vysledek, ale asi nebude potreba

        self.conn = None # Vzdalena console
        self.conn_pre = paramiko.SSHClient() # priprava pro vzdalenou consoli
        self.conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    #def _connect(self,ip,username,password):
        try:
            self.conn_pre.connect(ip,username,password)
        except paramiko.ssh_exception.AuthenticationExeption:
            print("chyba autentizace")
            return False
        self.conn = self.conn_pre.invoke_shell() 
        return True
    
    def _execCmd(self,command):
        #bude umet cist sekvenci prikazu
        self.conn.send(command)
        if conn.recv_ready():
            pass
        else:
            output = self.remote_conn.recv(5000)

class netconf():
    pass

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
