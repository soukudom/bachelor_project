#!/usr/bin/env python3
import device_modules._3com._3com4500 as _3com4500
import modules.connect
obj = _3com4500.vlan()
res = obj.vlan(**{'description': 'guest', 'id': 100})
print(res,obj.method)
