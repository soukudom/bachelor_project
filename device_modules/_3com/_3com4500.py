#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: Dominik Soukup

import modules.connect as connect

class DefaultConnection:
    def __init__(self):
        pass

class vlan:
    def __init__(self):
        pass

    def vlan(self, id="",description="",ip=""):
        pass

class interface:
    def __init__(self):
        pass

    def int(self, id="", description="", shutdown=""):
        pass

    def delete_int(self,id=""):
        pass

    def int_vlan(self,id="", mode="", allowed="", access=""):
        pass

    def int_agregate(self,id="",channel="",mode="",protocol=""):
        pass
