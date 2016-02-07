#!/usr/bin/env python3
from modules.connect import SSH

obj = SSH()

res=obj.connect("10.10.110.230",["root","Mazohi10"])
obj.doCommand(["show ip int br","c","show run"])
obj.disconnect()
print(res)
