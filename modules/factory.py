#!/usr/bin/env python3

import modules.fileProcessing as fp


class Factory:
    def getConfigProcessing(self, filename):
        return fp.ParseConfig(filename)

    def getDeviceProcessing(self, filename):
        return fp.ParseDevice(filename)

    def getSettingsProcessing(self, filename):
        return fp.ParseSettings(filename)
