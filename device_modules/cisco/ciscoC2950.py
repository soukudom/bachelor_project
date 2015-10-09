#!/usr/bin/env python3

def info():
    print("ahoj ja jsem cisco 2950")

class vlan:
    def __init__(self):
        self.method = "ssh"

    def vlan(self,id,description="",ip="",netmask=""):
        result = ["configure terminal"]
        result.append("interface vlan {}".format(id))
        if description:
            result.append("description {}".format(description))
        if ip and netmask:
            result.append("ip address {} {}".format(ip, netmask))
    
        return result 
        