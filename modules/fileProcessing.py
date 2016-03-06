#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Author: Dominik Soukup, soukudom@fit.cvut.cz

import yaml
import getpass
import sys
import re
from itertools import product
from copy import deepcopy
from abc import ABCMeta, abstractmethod


class ParseFile(metaclass=ABCMeta):
    def __init__(self, filename):
        #file checking if filename was loaded from settings file
        try:
            with open(filename, encoding="utf-8", mode="r"):
                pass
        except PermissionError:
            raise Exception("File '{}' can not be opened. Not enough permissions.".format(
                    filename))
        except FileNotFoundError:
            raise Exception("File '{}' does not exist".format(filename))
        except IsADirectoryError:
            raise Exception("File '{}' is a directory.".format(filename))
        except TypeError as e:
            raise Exception("Invalid file '{}'".format(filename))

    @abstractmethod
    def parse(self, filter):
        pass


class ParseDevice(ParseFile):
    def __init__(self, filename):
        #calling parents constructor
        super().__init__(filename)
        docu = ""       #loaded data from device file
        self.data = ""  #parsed YAML file to Python structure
        #loads YAML data
        try:
            with open(filename, encoding="utf-8", mode="r") as f:
                for i in f:
                    docu += i
            self.data = yaml.load(docu)
        except yaml.YAMLError as e:
            print("Error: Mistake in YAML syntax in '{}'".format(filename))
            print("For more infomation check log file")
            raise Exception(str(e))

    #checkes ip address format and unpack abbreviations
    def checkHost(self, hosts):
        configHost = {}  #result dictionary with concrete hosts and vendor(vendor is key)
        #go throught hosts
        for host in hosts:
            #split vendor name
            host = host.split(":")
            #checks ip address form
            if re.match("^([1-9][0-9]{0,2}\.){3}[1-9][0-9]{0,2}$", host[0]):
                #address is ok append to the ip pool
                if len(host) == 2:
                    try:
                        if host[0] in configHost[host[1]]:
                            print("Error: Duplicit ip address")
                            raise Exception("Duplicit ip address.")
                        configHost[host[1]].append(host[0])
                    #if the record is new
                    except KeyError:
                        configHost[host[1]] = []
                        configHost[host[1]].append(host[0])
                #manufactor was not inserted
                else:
                    print("Error: The manufactor was not specified in device file")
                    raise("The manufactor was not specified in device file")

            #unpack some abbreviations
            else:
                res = []  #result ip address pool
                tmp = ""  #help string for normat ip address part 
                #split accordint to octet
                parts = host[0].split(".")
                #check the form of ip address
                if len(parts) != 4:
                    print("Error: Invalid ip address, too less items")
                    raise Exception("Invalid ip address, too less items.")
                #checking individual octets
                for part in parts:
                    #if range was found
                    if re.match(
                            "^\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)$",
                            str(part)):
                        #remove bracket and splits according to numbers
                        part = part.strip(")(").split(",")
                        #if there are some ip already, add new octet to all
                        if res:
                            #help list variable for genereting ip addresses
                            res2 = []
                            for ip in res:
                                for i in range(
                                        int(part[0]), int(part[1]),
                                        int(part[2])):
                                    res2.append(ip + "." + str(i))
                            #replace temp variable to original
                            res = res2
                        #if there is only normal part of ip address, only add to result pool
                        elif tmp:
                            for i in range(
                                    int(part[0]), int(part[1]), int(part[2])):
                                res.append(tmp + "." + str(i))
                        else:
                            for i in range(int(part[0]),int(part[1]),int(part[2])):
                                res.append(str(i))

                    #sequece part
                    #similar process to range abbreviation
                    elif "," in str(part):
                        part = part.split(",")
                        if res:
                            res2 = []
                            for ip in res:
                                for i in part:
                                    try:
                                        int(i)
                                    except ValueError:
                                        print("Error: Bad value in sekvence")
                                        raise Exception("Bad value in sequece.")
                                    res2.append(ip + "." + str(i))
                            res = res2
                        elif tmp:
                            for i in part:
                                try:
                                    int(i)
                                except ValueError:
                                    print("Error: Bad value in sekvence")
                                    raise Exception("Bad value in sequence.")
                                res.append(tmp + "." + str(i))
                        else:
                            for i in part:
                                res.append(str(i))

                    #normal octed, only added to tmp variable
                    elif type(part) == type(str()):
                        if res:
                            #help list variable for genereting ip addresses
                            res2 = []
                            for ip in res:
                                res2.append(ip + "." + part)
                            #replace temp variable to original
                            res = res2
                        elif tmp:
                            tmp = tmp + "." + part
                        else:
                            tmp = part
                #append range to the ip pool
                if len(host) == 2:
                    for ip in res:
                        try:
                            if ip in configHost[host[1]]:
                                print("Error: Duplicit ip address")
                                raise Exception("Duplicit ip address.")
                            configHost[host[1]].append(ip)
                        except KeyError:
                            configHost[host[1]] = []
                            configHost[host[1]].append(ip)
                #manufactor was not inserted
                else:
                    print("Error: The manufactor was not specified")
                    raise Exception("The manufactor was not specified.")
        print(configHost)
        return configHost

    #returns list of device according to the group
    def parse(self, group):
        hosts = [] # list with host which was found
        try:
            if group == "":  #no filter was specified, all host will be returned:
                info = self.data #loaded YAML data
            #parses group hierarchy
            elif ":" in group:
                info = self.data
                keys = group.split(":")
                for i in keys:
                    #if key is number the type int is needed to filtering
                    try:
                        i = int(i)
                    except ValueError:
                        pass

                    info = info[i]
            #normal single key filter
            else:
                info = self.data[group]
        except KeyError as e:
            print("Wrong key")
            raise Exception("Wrong key in device file.")
        except TypeError:
            print("Bad device file format.")
            raise Exception("Bad device file format.")

        try:
            #recursive parsing
            while (type(list(info.values())[0])) == type(dict()):
                #in case of group hierarchy
                info = self.loop(info)

        except AttributeError:
            #in case of simple group name
            if type(info[0]) == type(str()):
                print("attribute error return", info)
                return self.checkHost(info)
            else:
                print("Bad device file format.")
                raise Exception("Bad device file format.")
        for szn in list(info.values()):
            #in case of more ip addresse in group
            for sz in szn:
                hosts.append(sz)
        return self.checkHost(hosts)

    #recursive loop in case of hierarchy group
    def loop(self, info):
        it = info.values().__iter__()
        pom = it.__next__()
        return pom


class ParseConfig(ParseFile):
    #loads config file and does YAML format check
    def __init__(self, filename):
        super().__init__(filename)
        docu = ""       #temp varible which stores YAML file
        self.data = ""  #parsed YAML file to Python structure  
        try:
            with open(filename, encoding="utf-8", mode="r") as f:
                for i in f:
                    docu += i
            self.data = yaml.load(docu)
        except Exception as e:
            print("Mistake in YAML syntax in '{}'".format(filename))
            print("For more infomation check log file")
            raise Exception(e)

    #parses single parts of config file and checks syntax
    def parse(self, filter):
        self.groupName = ""     # name of actual groupname in which I am during parsing
        self.className = ""     # name of actual classname is which I am during parsing
        self.methodName = ""    # name of actual methodname in which I am during parsing
        self.subMethodName = "" # name of actual submethodname in which I am during parsing
        self.methods = []       # final method which will be set up

        #recursive parse function
        self.rekurze(self.data, False, False, False, False, 0, None)
        return self.methods

    #checkes and upackes id value
    def checkId(self, name):
        ret = []    #temp variable
        buffer = [] #temp variable

        #lookes for id at the end of name 
        for i in reversed(name):
            try:
                int(i)
                buffer.insert(0, i)
            #if it is not simple number, tests abbreviation
            except Exception as e:
                tmp = re.search(
                    "\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)\s*?$",
                    name)
                if tmp is not None:
                    index = tmp.group(0)
                    buffer = index.strip("()").split(",")
                    for i in range(
                            int(buffer[0]), int(buffer[1]), int(buffer[2])):
                        ret.append(i)
                    return ret, name.split("(")[0], index #idNum, name, index
                else:
                    tmp = re.search(
                        #!!! umi detekovat jen 3, dodelat to co to vraci
                        "(^[^0-9]*)([0-9][0-9]*,[0-9][0-9]*,[0-9][0-9]*)",
                        name)
                    if tmp is not None:
                        index = tmp.group(2)
                        ret = index.split(",")
                        # print("sekvence",tmp.group(1),tmp.group(2))
                        return ret, tmp.group(1), index #idNum, name, index
                break
        #if nothing is satisfactory false is returned
        if not buffer:
            return False, None, "" #idNu, name, index
        #return founded number at the end of the function name
        else:
            tmp = "".join(buffer)
            return int(tmp), name.split(tmp)[0], tmp #idNum, name, index

    #unpackes abbreviation data
    def unpack(self,value):
        ret = []  # navratova hodnota

        #test the abbreviation
        try:
            value = value.strip()
            #range abbreviation
            if re.match(
                    "^\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)$",
                    str(value)):
                tmp = value.strip(")(").split(",")
                for i in range(int(tmp[0]), int(tmp[1]), int(tmp[2])):
                    ret.append(i)
                return ret  #, True

            # pokud se jedna o nazev se sekvenci
            elif re.search("\(.*?\)", str(value)):
                print("UNPACK S TADY S TOU ZKRATKOU JSEM NEPOCITAL")
            #    buffer = []
            #    # reg vyraz pro rozdelini retezce podle vice znaku
            #    tmp = re.split("\(|\)", value)
            #    for i in tmp[:-1]:
            #        if "," in i:
            #            buffer.append(i.split(","))
            #        else:
            #            buffer.append([i])
            #    for i in product(*buffer):
            #        ret.append(''.join(i))
            #    return ret  #, True

            #pokud se jedna pouze o sekvenci, tak vraci seznam
            #!!pohlidat jestli je to spravnej tvar
            #sequence abbreviation 
            elif "," in str(value):
                return value.split(",")  #, False

            #if nothing in satisfactory, original is returned
            else:
                return value  #, False
        except AttributeError:
            return value  #, False

    def rekurze(self, data, group, class_, method, subMethod, groupNum, idNum):
        groupLevel = group  #flag, which tells if group should be cut
        groupNumber = groupNum  # number of cut items
        class_ = class_  # flag which tells if the class space is left
        method = method  # flag, which tells if the method name space is left
        subMethod = subMethod  # flag, which tells if the submethod name space is left
        idNumb = "" #variable which contains interface number - there is used for submethod
        delete = []  # values which are neccessary to delete
        print(data)
        for i in data:
            print("data is loop:",i)
            try:
                # branch which parses list of tree
                if type(i) == type(str()):
                    #branch for next level of hierarchy (in that config case is it submethod)
                    #in that case submethod name will be longer 
                    #ready for next improvements
                    if type(data[i]) == type(dict()):
                        delete.append(i)
                        if self.subMethodName == "":
                            self.subMethodName = self.methodName + "_" + str(i)
                        else:
                            self.subMethodName = self.subMethodName + "_" + str(
                                i)
                        #DATA FORWARDING from method to submethod
                        #if is neccessary to send data from method to submethod, it can be done here
                        self.rekurze(data[i], False, False, False, True,
                                     groupNumber, idNum)
                    data[i] = self.unpack(data[i])
                    continue
                #branch for parsing group name
                elif list(i.keys())[0] == "group":
                    #if groupname is empty only add, in the other case add with :
                    if self.groupName == "":
                        self.groupName = str(i["group"][0]["name"])
                    else:
                        self.groupName += ":" + str(i["group"][0]["name"])
                    #save groupNumber, name and delete unnecessary group name
                    groupNumber = len(str(i["group"][0]["name"]).split(":"))
                    del i["group"][0]["name"]
                    self.rekurze(i["group"], True, False, False, False,
                                 groupNumber, None)
                # branch for parsing class and method name
                else:
                    if self.className == "":
                        self.className = list(i.keys())[0]
                        self.rekurze(i[self.className], False, True, False,
                                     False, groupNumber, None)

                    elif self.methodName == "":
                        self.methodName = list(i.keys())[0]
                        idNum, name, index = self.checkId(self.methodName)
                        if idNum:
                            self.methodName = name
                            self.rekurze(i[self.methodName + index], False,
                                         False, True, False, groupNumber,
                                         idNum)
                        else:
                            self.rekurze(i[self.methodName], False, False,
                                         True, False, groupNumber, idNum)

            except IndexError:
                continue
        # data modify at the end of cycle
        if class_:
            self.className = ""
            class_ = False
            return

        elif method:
            #deleting unnecessary keys form submethod
            for l in delete:
                del data[l]
            #save id number to data variable
            try:
                data["id"]
            except:
                #idNum added here, because I want to have all data together in data variable
                data["id"] = idNum
            ret = [self.groupName, self.className, self.methodName,
                   self.subMethodName, data]
            self.methods.append(ret)
            self.methodName = ""
            self.subMethodName = ""
            method = False
            return

        elif groupLevel:
            tmp = self.groupName.rsplit(":", groupNumber)
            if len(tmp) == 1 or groupNumber == len(self.groupName.split(":")):
                self.groupName = ""
            else:
                self.groupName = tmp[0]

        elif subMethod:
            data2 = deepcopy(data)
            data2["id"] = idNum  #idNum added here, because I wanto to have all data together in data variable
            ret = [self.groupName, self.className, self.methodName,
                   self.subMethodName, data2]
            self.methods.append(ret)
            data.clear()

            tmp = self.subMethodName.rsplit("_", 1)
            if len(tmp) == 1:
                self.subMethodName = ""
            else:
                self.subMethodName = tmp[0]
            subMethod = False


#finds out the global setting for program
class ParseSettings(ParseFile):
    def __init__(self, filename):
        super().__init__(filename)
        self.filename = filename
        self.settingsData = {} #parsed YAML file to Python structure

    #loads data from file
    def parse(self, filter):
        docu = "" #loaded data from YAML file 
        try:
            with open(self.filename, encoding="utf-8", mode="r") as f:
                for line in f:
                    docu += line
            self.settingsData = yaml.load(docu)

        except yaml.YAMLError as e:
            print("Bad YAML formating in '{}'".format(self.filename))
            raise Exception("Bad YAML formatting in '{}'".format(self.filename))

        #kontrola udaju
        #address, mask = self.settingsData["network"].split("/")
        ##print("testuju", type(address.strip()),"*")
        #if not re.match("^([1-9][0-9]{0,2}\.){3}[0-9]{0,3}$", address.strip()):
        #    print("bad network form")
        #    sys.exit(1)
        #try:
        #    mask = int(mask)
        #    if mask < 0 or mask > 32:
        #        print("bad mask")
        #        sys.exit(1)
        #except:
        #    print("Network mask form mistake")
        #    sys.exit(1)
        #
        #self.settingsData["network"] = address.strip()
        #self.settingsData["networkMask"] = mask
        #print("naparsoval jsem ", self.settingsData)
