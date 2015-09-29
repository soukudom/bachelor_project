#!/usr/bin/env pytho3
# -*- coding: utf-8 -*-

import paramiko
import time
import sys


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
    pass
