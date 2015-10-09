#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-

import paramiko
import time
import sys
from pysnmp.entity.rfc3413.oneliner import cmdgen


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
