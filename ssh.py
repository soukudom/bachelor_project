#!/usr/bin/env python3
from modules.connect import SSH

protocol = {"username": "root", "password": "Mazohi10", "ip": "10.10.110.230", "timeout": "5"}

obj = SSH(protocol)

res=obj.connect()
res2 = obj.doCommand(["show ip int br","show run"])
obj.disconnect()
print(res)
print(res2)
