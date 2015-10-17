#!/usr/bin/env python3

class vlan:
    def __init__(self):
        self.method = "netconf"
        self.hello = '<?xml version="1.0" encoding="UTF-8"?><hello><capabilities><capability>urn:ietf:params:netconf:base:1.0</capability><capability>urn:ietf:params:netconf:capability:writeable-running:1.0</capability><capability>urn:ietf:params:netconf:capability:startup:1.0</capability><capability>urn:ietf:params:netconf:capability:url:1.0</capability><capability>urn:cisco:params:netconf:capability:pi-data-model:1.0</capability><capability>urn:cisco:params:netconf:capability:notification:1.0</capability></capabilities></hello>]]>]]>'

    def vlan(self,id="",description="",ip="",shutdown=""):
        self.result = ""
        return self.result 

class interface:
    def __init__(self):
        self.method = "netconf"
        self.hello = '<?xml version="1.0" encoding="UTF-8"?><hello><capabilities><capability>urn:ietf:params:netconf:base:1.0</capability><capability>urn:ietf:params:netconf:capability:writeable-running:1.0</capability><capability>urn:ietf:params:netconf:capability:startup:1.0</capability><capability>urn:ietf:params:netconf:capability:url:1.0</capability><capability>urn:cisco:params:netconf:capability:pi-data-model:1.0</capability><capability>urn:cisco:params:netconf:capability:notification:1.0</capability></capabilities></hello>]]>]]>'
    
    def int(self, id="", description = "", shutdown="",):
        self.result = ""
        return self.result 

    
    def int_vlan(self,id="",mode="",allowed="", access=""):
        self.result = ""
        return self.result 
    
    def int_agregate(self,id="",protocol="",channel="",mode=""):
        self.result = ""
        return self.result 

    def default(self, id="", shutdown="", description=""):
        self.result = ""
        return self.result 
    
    def default_vlan(self,id="", mode="", access="", allowed=""):
        self.result = ""
        return self.result 

    def mac(self, id="", description = "", shutdown=""):
        self.result = ""
        return self.result 
    
    def mac_vlan(self, id="", mode="", allowed="", access=""):
        self.result = ""
        return self.result 

    def mac_agregate(self,id="",protocol="",channel="", mode=""):
        self.result = ""
        return self.result 
