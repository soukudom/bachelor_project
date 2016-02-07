#!/usr/bin/env python3

from modules.connect import SNMP

obj = SNMP()

res = obj.connect("10.10.110.220","sin",None)

print(res)
