#!/usr/bin/env python3
# sax xml, libxml - moduly pro praci s xml

from modules.connect import netconf as netconf
#import paramiko
#import time

#conn_pre = paramiko.SSHClient()
#conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#conn_pre.connect("-s 10.10.110.51 netconf",username="root",password="Mazohi10",look_for_keys=False, allow_agent=False)
#conn = conn_pre.invoke_shell()
#time.sleep(0.5)
#output = conn.recv(100)
#print("prihlasil jsem se na", output)

hello='<?xml version="1.0" encoding="UTF-8"?><hello><capabilities><capability>urn:ietf:params:netconf:base:1.0</capability><capability>urn:ietf:params:netconf:capability:writeable-running:1.0</capability><capability>urn:ietf:params:netconf:capability:startup:1.0</capability><capability>urn:ietf:params:netconf:capability:url:1.0</capability><capability>urn:cisco:params:netconf:capability:pi-data-model:1.0</capability><capability>urn:cisco:params:netconf:capability:notification:1.0</capability></capabilities></hello>]]>]]>'
meth='<?xml version="1.0" encoding="UTF-8"?><rpc message-id="105"xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><get-config><source><running/></source><filter><config-format-text-block><text-filter-spec>interface GigabitEthernet1/0/1</text-filter-spec></config-format-text-block></filter></get-config></rpc>]]>]]>'
obj = netconf()
obj._connect("10.10.110.51","root","Mazohi10",hello)
obj._execCmd(meth)
