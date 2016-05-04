#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################
# Author: Dominik Soukup, soukudom@fit.cvut.cz #
################################################

import modules.fileProcessing as fp

# \cl factory pattern class
class Factory:
    # \fn configurations file instance
    # \return ParseConfig object
    def getConfigProcessing(self, filename):
        return fp.ParseConfig(filename)

    # \fn device file instance
    # \return ParseDevice object
    def getDeviceProcessing(self, filename):
        return fp.ParseDevice(filename)

    # \fn settings file instance
    # \return ParseSettings object
    def getSettingsProcessing(self, filename):
        return fp.ParseSettings(filename)
