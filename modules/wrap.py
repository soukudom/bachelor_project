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

        self._rekurze(self.data, False, False, False)
        sys.exit(1)
        for i in self.data:
            if list(i.keys())[0] == "group":
            # najdi si skupinu
            # dej mi jmeno skupiny
                self.groupName = i["group"][0]["name"]
                del i["group"][0]["name"]
                for j in i["group"]:
                        
                    #ziskej jmena trid 
                    try:
                        if list(j.keys())[0] == "group":
                            #zpracuj skupinu
                            pass
                        else:
                            
                            self.className = list(j.keys())[0]
                            print("jmeno tridy:",self.className)
                            for k in j[self.className]:
                                print(k)
                    except IndexError:
                        continue
                    except Exception as e:
                        print(e)
            else:
                pass
            #pokracuj pro vsechny
            sys.exit(1)
    # vymazavat promenny jmena a projit si az do konce
    def _rekurze(self, data, group, class_, method):
        groupLevel = group
        group = False
        class_ = class_
        method = method
        
        
        for i in data:
            print("hodnoty:",groupLevel, class_,method)
            #if class_:
            #    print("resetuju class a na zacatku")
            #    self.className = ""
            #elif method:
            #    print("resetuju method na zacatku")
            #    self.methodName = ""

            print("prvni prvek z foru:", i)
            input("stiskni enter")
            try:
                if type(i) == type(str()):
                    #method = True
                    print("dosel jsem ke konci")
                    #for m in data.values():
                    #   print(m,type(m))
                    print(i)
                    continue
                #try:
                elif list(i.keys())[0] == "group":
    # pridavani jmena grupy dobry, ale odebirani jmena udelat podle posledniho jmena v parametru name, tzn odebrat treba vic levelu najednou jako je u sin:48

                    if self.groupName == "":
                        print("nastavuju group 1")
                        self.groupName = i["group"][0]["name"]
                        group = True
                    #elif group:
                    #    print("nastavuju group 2")
                    #    self.groupName = self.groupName.rsplit(":",1)[0]
                    #    self.groupName += ":"+str(i["group"][0]["name"])
                    else:
                        print("nastavuju group 3")
                        self.groupName += ":"+str(i["group"][0]["name"])
                        group = True

                    del i["group"][0]["name"]
                    print("nasel jsem group",self.groupName ,"dalsi kolo:",i["group"])
                        #group = True
                    input("stiskni enter")
                    self._rekurze(i["group"],True,False,False) 
                #except IndexError:
                #   continue
                else:
                    if self.className == "":
                        self.className = list(i.keys())[0]
                        print("nasel jsem tridu",self.className ," dalsi kolo:",i[self.className])
                        input("stiskni enter")
                        #class_ = True
                        self._rekurze(i[self.className],False,True,False)

                    elif self.methodName == "":
                        self.methodName = list(i.keys())[0]
                        print("nasel jsem metodu",self.methodName," dalsi kolo:",i[self.methodName])
                        #method = True
                        input("stiskni enter")
                        #print("hodnoty", group,class_,method)
                        self._rekurze(i[self.methodName],False,False,True)
            except IndexError:
                continue
            
                #elif True:
                #    print(i)
                #    print("jsem na konci")
                #    continue
        print("jdu pryc z foru", groupLevel, class_, method)
        if class_:
            print("resetuju class a vracim se")
            self.className = ""
            class_ = False
            return
        elif method:
            print("resetuju method a vracim se")
            self.methodName = ""
            method = False
            #class_ = True
            return
        elif groupLevel:
            tmp = self.groupName.rsplit(":",1)
            if len(tmp) == 1:
                self.groupName = ""
            else:
                self.groupName = self.groupName.rsplit(":",1)[0]
            print("menim groupName na:", self.groupName) 
                
 
