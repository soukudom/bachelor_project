#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import getpass
import sys
import re
from itertools import product
from copy import deepcopy
from abc import ABCMeta, abstractmethod


class ParseFile(metaclass=ABCMeta):
    def __init__(self, filename):
        #kontrola souboru, pokud jsou nacitany pomoci konfiguracniho souboru
        try:
            #print("init testing")
            with open(filename, encoding="utf-8", mode="r"):
                pass
        except PermissionError:
            #print(
            #    "File '{}' can not be opened. Not enough permissions.".format(
            #        filename))
            raise Exception("File '{}' can not be opened. Not enough permissions.".format(
                    filename))
            #sys.exit(1)
        except FileNotFoundError:
            #print("File '{}' does not exist".format(filename))
            raise Exception("File '{}' does not exist".format(filename))
            #sys.exit(1)
        except IsADirectoryError:
            #print("File '{}' is a directory.".format(filename))
            raise Exception("File '{}' is a directory.".format(filename))
            #sys.exit(1)
        except TypeError as e:
            #print("Invalid file '{}'".format(filename))
            raise Exception("Invalid file '{}'".format(filename))
            #sys.exit(1)

    @abstractmethod
    def parse(self, filter):
        pass


class ParseDevice(ParseFile):
    def __init__(self, filename):
        super().__init__(filename)
        docu = ""
        self.data = ""  # nactena data z configu
        self.hosts = []  #  nalezena zarizeni
        try:
            with open(filename, encoding="utf-8", mode="r") as f:
                for i in f:
                    docu += i
            self.data = yaml.load(docu)
        except yaml.YAMLError as e:
            print("Mistake in YAML syntax in '{}'".format(filename))
            print("For more infomation check log file")
            raise Exception(str(e))
            #sys.exit(1)

            #kontroluje spravnost ip address a rozbaluje zkratky
    def checkHost(self, hosts):
        configHost = {
        }  # vysledny slovnik s konkretnimy hosty, klicem prislusny vendor
        #prochazim vybranou skupinu hostu
        for host in hosts:
            #oddeleni nazvu vyrobce
            host = host.split(":")
            #kontrola tvaru ip adresy
            if re.match("^([1-9][0-9]{0,2}\.){3}[1-9][0-9]{0,2}$", host[0]):
                if len(host) == 2:
                    try:
                        if host[0] in configHost[host[1]]:
                            print("duplicit ip address")
                            #sys.exit(1)
                            raise Exception("Duplicit ip address.")
                        configHost[host[1]].append(host[0])
                    except KeyError:
                        configHost[host[1]] = []
                        configHost[host[1]].append(host[0])

                else:
                    print("The manufactor was not specified")
                    #sys.exit(1)
                    raise("The manufactor was not specified")

            # pokud neproslo jedna se o nejakou sekvenci
            else:
                res = []  # vysledny seznam ip adres
                tmp = ""  #pomocny retezev pro normalni casti ip adresy
                # rozdeleni podle oktetu
                parts = host[0].split(".")
                #kontrola tvaru ip adresy
                if len(parts) != 4:
                    print("invalid ip address, too less items")
                    #exit(1)
                    raise Exception("Invalid ip address, too less items.")
                #kontrola jednotlivych oktetu ip adresy
                for part in parts:
                    #pokud jsem nalezl range
                    if re.match(
                            "^\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)$",
                            str(part)):
                        #odstranim zavorky a rozdelim po cislech
                        part = part.strip(")(").split(",")
                        #jestli ve vysledne seznamu adresy jsou, tak je rozmnozim
                        if res:
                            # pomocne pole na uchovani novych adres
                            res2 = []
                            for ip in res:
                                for i in range(
                                        int(part[0]), int(part[1]),
                                        int(part[2])):
                                    res2.append(ip + "." + str(i))
                            #nahrada starych adres za nove
                            res = res2
                        #pokam mam jenom normalni adresu tak pridam rovnou do vysledneho seznamu
                        elif tmp:
                            for i in range(
                                    int(part[0]), int(part[1]), int(part[2])):
                                res.append(tmp + "." + str(i))
                        #!!pridat vetev kdy jeste nemam ani tmp

                        #pokud jsem nasel sekvenci
                        #podobny proces jako u range
                    elif "," in str(part):
                        part = part.split(",")

                        if res:
                            res2 = []
                            for ip in res:
                                for i in part:
                                    try:
                                        int(i)
                                    except ValueError:
                                        print("bad value in sekvence")
                                        #exit(1)
                                        raise Exception("Bad value in sequece.")
                                    res2.append(ip + "." + str(i))
                            res = res2
                        elif tmp:
                            for i in part:
                                try:
                                    int(i)
                                except ValueError:
                                    print("bad value in sekvence")
                                    #exit(1)
                                    raise Exception("Bad value in sequence.")
                                res.append(tmp + "." + str(i))
                    #pridani oktetu do pomocneho tmp
                    elif type(part) == type(str()):
                        if tmp:
                            tmp = tmp + "." + part
                        else:
                            tmp = part

                if len(host) == 2:
                    for ip in res:
                        try:
                            if ip in configHost[host[1]]:
                                print("duplicit ip address")
                                #sys.exit(1)
                                raise Exception("Duplicit ip address.")
                            configHost[host[1]].append(ip)
                        except KeyError:
                            configHost[host[1]] = []
                            configHost[host[1]].append(ip)
                #pokud nebyl zadan vyrobce
                else:
                    print("The manufactor was not specified")
                    #sys.exit(1)
                    raise Exception("The manufactor was not specified.")

        return configHost

    # vraci seznam zadanych zarizeni podle skupiny
    def parse(self, group):
        hosts = []
        try:
            if group == "":  #nahrada "all":
                info = self.data
            elif ":" in group:
                info = self.data
                keys = group.split(":")
                for i in keys:
                    try:
                        i = int(i)
                    except ValueError:
                        pass

                    info = info[i]
            else:
                info = self.data[group]
        except KeyError:
            print("Wrong key")
            #exit(1)
            raise Exception("Wrong key in device file")
        except TypeError:
            print("Bad device file format.")
            #exit(1)
            raise Exception("Bad device file format.")

        try:
            while (type(list(info.values())[0])) == type(dict()):
                info = self.loop(info)

        except AttributeError:
            if type(info[0]) == type(str()):
                return self.checkHost(info)
            else:
                print("Bad device file format.")
                #exit(1)
                raise Exception("Bad device file format.")
        for szn in list(info.values()):
            for sz in szn:
                hosts.append(sz)
        return self.checkHost(hosts)

    # rekurzivni pruchod
    def loop(self, info):
        it = info.values().__iter__()
        pom = it.__next__()
        #print("metoda loop vraci ", pom)
        return pom

    #def getManufactor(self,protocol,vendor):
    #    #naimportuju defaultni parsovaci tridu a zavolam metodu
    #    module = "device_modules.{}.{}".format(vendor,vendor)
    #    importObj = importlib.import_module(module)
    #    obj = getattr(importObj,"Device")
    #    objInst = obj()
    #    #manufactor = objInst.getDeviceName(ip_address,community,"get")
    #    #print("ptam se na vendora: ",protocol)
    #    manufactor = objInst.getDeviceName(protocol)
    #    return manufactor


class ParseConfig(ParseFile):
    #nacte konfiguracni soubor, a provede kontrolu formatu yaml
    def __init__(self, filename):
        super().__init__(filename)
        docu = ""
        self.data = ""
        try:
            with open(filename, encoding="utf-8", mode="r") as f:
                for i in f:
                    docu += i
            self.data = yaml.load(docu)
        except Exception as e:
            print("Mistake in YAML syntax in '{}'".format(filename))
            print("For more infomation check log file")
            #sys.exit(1)
            raise Exception(e)
            #print(e) #!! pridat log file

            #parsuje jednotlive casti kofiguracniho souboru, kontroluje syntaxy
    def parse(self, filter):
        #print("metoda parse v config parseru")
        self.groupName = ""  # nazev skupiny, ve ktere se aktualne nachazim
        self.className = ""  # nazev tridy, kde se aktualne nachazim
        self.methodName = ""  # nazev metody, kde se aktualne nachazim
        self.subMethodName = ""  # nazev submetody, kde se aktualne nachazim
        self.methods = []  # metody pro nastaveni

        # funkce ktere rekurzivne prochazi konfiguracni soubor
        self.rekurze(self.data, False, False, False, False, 0, None)
        print("metody",self.methods)
        return self.methods

    #kotroluje a rozbaluje id hodnotu u jmena metody, cislo je tady aby se odlisilo vice metod najednou
    def checkId(self, name):
        ret = []  # vystupni seznam prvku
        buffer = []  # vystupni seznam prvku

        # nejprve kontrola cisla na konci nazvu metody
        for i in reversed(name):
            try:
                int(i)
                buffer.insert(0, i)
            # pokud se nejedna o cislo, testuje se pritomnost range
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
                    # nasla se range a vraci se seznam
                    #print("vracim:", ret, name.split("(")[0], index)
                    return ret, name.split("(")[0], index
                ###NEW !!ohlidat aby tam mohli bejt presne 3 cisla
                else:
                    tmp = re.search(
                        "(^[^0-9]*)([0-9][0-9]*,[0-9][0-9]*,[0-9][0-9]*$)",
                        name)
                    if tmp is not None:
                        index = tmp.group(2)
                        ret = index.split(",")
                        # print("sekvence",tmp.group(1),tmp.group(2))
                        return ret, tmp.group(1), index
                ##END NEW !!
                break
        # jestlize nevyhovuje ani jeden vzor, tak se vraci priznak false
        if not buffer:
            return False, None, ""
        # vraci se nalezene cislo na konci nazvu funkce
        else:
            tmp = "".join(buffer)
            return int(tmp), name.split(tmp)[0], tmp

    # rozbaluje zkracene hodnoty pro nastaveni
    def unpack(self,
               value):  #!!! doufam ze reg vyrazy, fungujou jeste otestovat
        ret = []  # navratova hodnota

        #testuje pokud se jedna o sekvenci
        try:
            value = value.strip()
            if re.match(
                    "^\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)$",
                    str(value)):
                tmp = value.strip(")(").split(",")
                for i in range(int(tmp[0]), int(tmp[1]), int(tmp[2])):
                    ret.append(i)
                #print("rozbaluji range v hodnote", ret)
                return ret  #, True

            # pokud se jedna o nazev se sekvenci
            elif re.search("\(.*?\)", str(value)):
                buffer = []
                # reg vyraz pro rozdelini retezce podle vice znaku
                tmp = re.split("\(|\)", value)
                for i in tmp[:-1]:
                    if "," in i:
                        buffer.append(i.split(","))
                    else:
                        buffer.append([i])
                for i in product(*buffer):
                    ret.append(''.join(i))
                return ret  #, True

            #pokud se jedna pouze o sekvenci, tak vraci seznam
            #!!pohlidat jestli je to spravnej tvar
            elif "," in str(value):
                return value.split(",")  #, False

            #pokud nevyhovuje ani jeden vzor, tak vrati original
            else:
                return value  #, False
        except AttributeError:
            return value  #, False

    def rekurze(self, data, group, class_, method, subMethod, groupNum, idNum):
        groupLevel = group  # flag, ktery rika jestli mam odpojovat skupinu
        groupNumber = groupNum  # pocet prvku skupiny, pro odebirani
        class_ = class_  # flag, ktery rika jestli vyskakuju ze tridy
        method = method  # flag, ktery rika jeslti vyskakuju z metody
        subMethod = subMethod  # flag, ktery mi rika jestli vyskakuju z podmetody
        #idNum promena, ktera obsahuje identifikator rozhrani
        #mohl bych ji sem taky pro prehlednost pridat
        delete = []  # hodnoty, ktere je treba vymazat

        for i in data:
            try:
                # vetev pro parsovani listu
                if type(i) == type(str()):
                    # vetev pro dalsi cleneni funkci
                    if type(data[i]) == type(dict()):
                        delete.append(i)
                        if self.subMethodName == "":
                            self.subMethodName = self.methodName + "_" + str(i)
                        else:
                            self.subMethodName = self.subMethodName + "_" + str(
                                i)
                        #!! pokud chci naky hodnoty preposlat do subMethody tak musim pridat tady, takle muzu dorucit treba mac adresu
                        self.rekurze(data[i], False, False, False, True,
                                     groupNumber, idNum)
                    data[i] = self.unpack(data[i])
                    #print("ukladam",i,data[i])
                    continue
                # vetev pro parsovani nazvu group
                elif list(i.keys())[0] == "group":

                    if self.groupName == "":
                        self.groupName = str(i["group"][0]["name"])
                    else:
                        self.groupName += ":" + str(i["group"][0]["name"])

                    groupNumber = len(str(i["group"][0]["name"]).split(":"))
                    del i["group"][0]["name"]
                    self.rekurze(i["group"], True, False, False, False,
                                 groupNumber, None)
                # vetev pro parsovani nazvu tridy a metody
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
                #print("vyjimka index error")
                continue
        # uprava potrebnych hodnot po skonceni cyklu
        if class_:
            self.className = ""
            class_ = False
            return

        elif method:
            #mazani nepotrebnych klicu z subMethod
            for l in delete:
                del data[l]
            #abych si nepremazaval klic kdyz uz tam je
            try:
                data["id"]
            except:
                data[
                    "id"] = idNum  #pridal jsem aby byly vsechny argumenty pohromade
            #!odstranit to idnum melo by fungovat
            #ret = [self.groupName,self.className,self.methodName, self.subMethodName, idNum ,data]
            ret = [self.groupName, self.className, self.methodName,
                   self.subMethodName, data]
            self.methods.append(ret)
            self.methodName = ""
            self.subMethodName = ""
            method = False
            return

        elif groupLevel:
            #print("cislo skupiny",groupNumber)
            tmp = self.groupName.rsplit(":", groupNumber)
            if len(tmp) == 1 or groupNumber == len(self.groupName.split(":")):
                self.groupName = ""
            else:
                self.groupName = tmp[0]

        elif subMethod:
            data2 = deepcopy(data)
            data2[
                "id"] = idNum  #pridal jsem aby byly vsechny argumenty pohromade
            #!odstranit to idnum # melo by fungovat 
            #ret = [self.groupName,self.className, self.methodName,self.subMethodName, idNum ,data2]
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


    #zjisti nastaveni aplikace
class ParseSettings(ParseFile):
    def __init__(self, filename):
        super().__init__(filename)
        self.filename = filename
        self.settingsData = {}

    def parse(self, filter):
        #nacteni dat ze souboru
        docu = ""
        try:
            with open(self.filename, encoding="utf-8", mode="r") as f:
                for line in f:
                    docu += line
            self.settingsData = yaml.load(docu)

        except yaml.YAMLError as e:
            print("Bad YAML formating in '{}'".format(self.filename))
            #sys.exit(1)
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
