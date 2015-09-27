#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import sys

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

    def _neco(self):
        self.groupName = ""
        self.className = ""
        self.methodName = ""
        self.subMethodName = ""

        self._rekurze(self.data, False, False, False,False,0)
        sys.exit(1)

    def _rekurze(self, data, group, class_, method, subMethod,groupNum):
        groupLevel = group # flag, ktery rika jestli mam odpojovat skupinu
        groupNumber = groupNum # pocet prvku skupiny, pro odebirani
        class_ = class_ # flag, ktery rika jestli vyskakuju ze tridy
        method = method # flag, ktery rika jeslti vyskakuju z metody
        subMethod = subMethod # flag, ktery mi rika jestli vyskakuju z podmetody
        
        
        for i in data:
            #print("prvni prvek z foru:", i)
            input("stiskni enter")
            try:
                if type(i) == type(str()):
                    #print("dosel jsem ke konci")
                    print("klic:",i," hodnota:",data[i])
                    if type(data[i]) == type(dict()):
                        if self.subMethodName == "":
                            self.subMethodName = self.methodName+"_"+str(i)
                        else:
                            self.subMethodName = self.subMethodName+"_"+str(i)
                        print("nasel jse m submethod",self.subMethodName)
                        self._rekurze(data[i],False,False,False,True,groupNumber)
                    #for m in data.values():
                    #   print(m,type(m))
                    continue
                elif list(i.keys())[0] == "group":

                    if self.groupName == "":
                     #   print("nastavuju group 1")
                        self.groupName = str(i["group"][0]["name"])
                    else:
                      #  print("nastavuju group 3")
                        self.groupName += ":"+str(i["group"][0]["name"])

                    groupNumber = len(str(i["group"][0]["name"]).split(":"))
                    del i["group"][0]["name"]
                    #print("nasel jsem group",self.groupName ,"dalsi kolo:",i["group"])
                    print("nasel jsem group",self.groupName)
                    input("stiskni enter")
                    self._rekurze(i["group"],True,False,False,False,groupNumber) 
                else:
                    if self.className == "":
                        self.className = list(i.keys())[0]
                        #print("nasel jsem tridu",self.className ," dalsi kolo:",i[self.className])
                        print("nasel jsem tridu",self.className)
                        input("stiskni enter")
                        #class_ = True
                        self._rekurze(i[self.className],False,True,False,False,groupNumber)

                    elif self.methodName == "":
                        self.methodName = list(i.keys())[0]
                        #print("nasel jsem metodu",self.methodName," dalsi kolo:",i[self.methodName])
                        print("nasel jsem metodu",self.methodName)
                        input("stiskni enter")
                        self._rekurze(i[self.methodName],False,False,True,False,groupNumber)
            except IndexError:
                continue
            
        print("jdu pryc z foru", groupLevel, class_, method)
        if class_:
            #print("resetuju class a vracim se")
            self.className = ""
            class_ = False
            return
        elif method:
            #print("resetuju method a vracim se")
            self.methodName = ""
            method = False
            #class_ = True
            print("moje zkontrolovana data jsou:" )
            for k in data:
                print(k,":",data[k])
            return
        elif groupLevel:
            #print("cislo skupiny",groupNumber)
            tmp = self.groupName.rsplit(":",groupNumber)
            if len(tmp) == 1 or groupNumber == len(self.groupName.split(":")):
                self.groupName = ""
            else:
                self.groupName = tmp[0] 
            #print("menim groupName na:", self.groupName) 
        elif subMethod:
            tmp = self.subMethodName.rsplit("_",1)
            if len(tmp) == 1:
                self.subMethodName = ""
            else:
                self.subMethodName = tmp[0]
            subMethod = False
            
            
                
 
