#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import sys
import re
from itertools import product
from copy import deepcopy

#!!! upravit
#!!!  pridat metodu getManufactor
class parseDevice:
    def __init__(self, filename, group):
        docu = ""
        self.data = "" 
        try:
            with open(filename, encoding="utf-8", mode="r") as f:
                for i in f:
                    docu += i
            self.data=yaml.load(docu)
        except Exception as e:
            print(e)

    # puvodni loop
    def _getHosts(self, info):
        hosts = []
        while(type(list(info.values())[0])) == type(dict()):
            info=self.loop(info)
        for szn in list(info.values()):
            for sz in szn:
                hosts.append(sz)
        return hosts 

    # to je puvodni ref_loop pro rekurzivni smycku
    def loop(self,info):
        it = info.values().__iter__()
        pom = it.__next__()
        return pom
        
class parseConfig:
    #nacte konfiguracni soubor, a provede kontrolu formatu yaml
    def __init__(self, filename):
        docu = ""
        self.data = "" 
        try:
            with open(filename, encoding="utf-8", mode="r") as f:
                for i in f:
                    docu += i
            self.data=yaml.load(docu)
        except Exception as e:
            print(e)

    #parsuje jednotlive casti kofiguracniho souboru, kontroluje syntaxy
    def _parse(self):
        self.groupName = "" #nazev skupiny, ve ktere se aktualne nachazim
        self.className = "" # nazev tridy, kde se aktualne nachazim
        self.methodName = "" # nazev metody, kde se aktualne nachazim
        self.subMethodName = "" # nazev submetody, kde se aktualne nachazim
        self.methods = [] #metody pro nastaveni
            
        # funkce ktere rekurzivne prochazi konfiguracni soubor
        self._rekurze(self.data, False, False, False,False,0,None)
        for i in self.methods:
            print(i)    

    #kotroluje a rozbaluje id hodnotu u jmena metody, cislo je tady aby se odlisilo vice metod najednou
    def _checkId(self,name):
        ret = [] # vystupni seznam prvku
        buffer = [] # vystupni seznam prvku

        # nejprve kontrola cislo na konci nazvu metody
        for i in reversed(name):
            try:
                int(i)
                buffer.insert(0,i)
            # pokud se nejedna o cislo, testuje se pritomnost sekvence
            except Exception as e:
                tmp = re.search("\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)\s*?$",name)
                if tmp is not None:
                    index = tmp.group(0)
                    buffer = index.strip("()").split(",")
                    for i in range(int(buffer[0]),int(buffer[1]),int(buffer[2])):
                        ret.append(i)        
                    # nasla se range a vraci se seznam
                    return ret, name.split("(")[0], index
                break
        # jestlize nevyhovuje ani jeden vzor, tak se vraci priznak false 
        if not buffer:
            return False, None, ""
        # vraci se nalezene cislo na konci nazvu funkce
        else:
            tmp = "".join(buffer)
            return int(tmp), name.split(tmp)[0], tmp

    # rozbaluje zkracene hodnoty pro nastaveni
    def _unpack(self, value): #!!! doufam ze reg vyrazy, fungujou jeste otestovat
        ret = [] # navratova hodnota

        #testuje pokud se jedna o sekvenci
        try:
            value = value.strip()
            if re.match("^\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)$",str(value)):
                tmp = value.strip(")(").split(",")
                for i in range(int(tmp[0]),int(tmp[1]),int(tmp[2])):
                    ret.append(i)
                return ret#, True 

            # pokud se jedna o nazev se sekvenci
            elif re.search("\(.*?\)",str(value)):
                buffer = []
                # reg vyraz pro rozdelini retezce podle vice znaku
                tmp = re.split("\(|\)",value)
                for i in tmp[:-1]:
                    if "," in i:
                        buffer.append(i.split(","))
                    else:
                        buffer.append([i])
                for i in product(*buffer):
                    ret.append(''.join(i))
                return ret#, True

            #pokud se jedna pouze o sekvenci, tak vraci seznam
            elif "," in str(value):
                return value.split(",")#, False

            #pokud nevyhovuje ani jeden vzor, tak vrati original
            else:
                return value#, False
        except AttributeError:
            return value#, False
    
            

    def _rekurze(self, data, group, class_, method, subMethod,groupNum,idNum):
        groupLevel = group # flag, ktery rika jestli mam odpojovat skupinu
        groupNumber = groupNum # pocet prvku skupiny, pro odebirani
        class_ = class_ # flag, ktery rika jestli vyskakuju ze tridy
        method = method # flag, ktery rika jeslti vyskakuju z metody
        subMethod = subMethod # flag, ktery mi rika jestli vyskakuju z podmetody
        #idNum promena, ktera obsahuje identifikator rozhrani
        #mohl bych ji sem taky pro prehlednost pridat
        delete = [] # hodnoty, ktere je treba vymazat 

        for i in data:
            try:
                # vetev pro parsovani listu
                if type(i) == type(str()):
                    # vetec pro dalsi cleneni funkci
                    if type(data[i]) == type(dict()):
                        delete.append(i)
                        if self.subMethodName == "":
                            self.subMethodName = self.methodName+"_"+str(i)
                        else:
                            self.subMethodName = self.subMethodName+"_"+str(i)
                        #!! pokud chci naky hodnoty preposlat do subMethody tak musim pridat tady, takle muzu dorucit treba mac adresu
                        self._rekurze(data[i],False,False,False,True,groupNumber,idNum)
                    data[i] = self._unpack(data[i])
                    continue
                # vetev pro parsovani nazvu group
                elif list(i.keys())[0] == "group":

                    if self.groupName == "":
                        self.groupName = str(i["group"][0]["name"])
                    else:
                        self.groupName += ":"+str(i["group"][0]["name"])

                    groupNumber = len(str(i["group"][0]["name"]).split(":"))
                    del i["group"][0]["name"]
                    self._rekurze(i["group"],True,False,False,False,groupNumber,None) 
                # vete pro parsovani nazvu tridy a metody
                else:
                    if self.className == "":
                        self.className = list(i.keys())[0]
                        self._rekurze(i[self.className],False,True,False,False,groupNumber,None)

                    elif self.methodName == "":
                        self.methodName = list(i.keys())[0]
                        idNum,name,index = self._checkId(self.methodName)
                        if idNum:
                            self.methodName = name
                            self._rekurze(i[self.methodName+index],False,False,True,False,groupNumber,idNum)
                        else:
                            self._rekurze(i[self.methodName],False,False,True,False,groupNumber,idNum)
                            
            except IndexError:
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
            ret = [self.groupName,self.className,self.methodName, self.subMethodName, idNum ,data]
            self.methods.append(ret)
            self.methodName = ""
            self.subMethodName = ""
            method = False
            return

        elif groupLevel:
            #print("cislo skupiny",groupNumber)
            tmp = self.groupName.rsplit(":",groupNumber)
            if len(tmp) == 1 or groupNumber == len(self.groupName.split(":")):
                self.groupName = ""
            else:
                self.groupName = tmp[0] 

        elif subMethod:
            data2 = deepcopy(data)
            ret = [self.groupName,self.className, self.methodName,self.subMethodName, idNum ,data2]
            self.methods.append(ret)
            data.clear()

            tmp = self.subMethodName.rsplit("_",1)
            if len(tmp) == 1:
                self.subMethodName = ""
            else:
                self.subMethodName = tmp[0]
            subMethod = False
            
class _orchestrate():    
    pass                 
 
