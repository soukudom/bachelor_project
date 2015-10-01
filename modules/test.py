#!/usr/bin/env python3

from connect import snmp

val = snmp()
print(snmp()._snmpGet("10.10.110.51","sin","sysDescr"))
print("ahoj")
