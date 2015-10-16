#!/usr/bin/env python3
# sax xml, libxml - moduly pro praci s xml
import importlib

mod = "device_modules.cisco.ciscoC2950"
a = importlib.import_module(mod)

res = getattr(a,"info")
obj = res()
obj.info()
#res.info()
#print(res)



