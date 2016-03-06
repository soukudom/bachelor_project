#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: Dominik Soukup, soukudom@fit.cvut.cz


import modules.fileProcessing as fp


class Factory:
    def getConfigProcessing(self, filename):
        return fp.ParseConfig(filename)

    def getDeviceProcessing(self, filename):
        return fp.ParseDevice(filename)

    def getSettingsProcessing(self, filename):
        return fp.ParseSettings(filename)
