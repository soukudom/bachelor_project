#!/usr/bin/env python3
import device_modules.cisco.ciscoC2950 as ciscoC2950
obj = ciscoC2950.vlan()
res = obj.vlan(**{'id': 100, 'description': 'guest'})
print(res,obj.method)