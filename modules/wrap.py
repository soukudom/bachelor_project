#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import sys
import re
from itertools import product


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
            
        # funkce ktere rekurzivne prochazi konfiguracni soubor
        self._rekurze(self.data, False, False, False,False,0,None)
        #sys.exit(1)

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
    def _unpack(self, value): #!!! podivat se na reg vyrazi, jestli se jeste nedaj napsat jinak, a hlavne tam dam libovolny pocet bilych znaku
        ret = [] # navratova hodnota

        #testuje pokud se jedna o sekvenci
        try:
            value = value.strip()
            print(value, type(value))
            if re.match("^\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)$",str(value)):
                tmp = value.strip(")(").split(",")
                for i in range(int(tmp[0]),int(tmp[1]),int(tmp[2])):
                    ret.append(i)
                print("return True, typ range")
                return ret#, True 

            # pokud se jedna o nazev se sekvenci
            elif re.search("\(\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?,\s*?[1-9][0-9]*?\s*?\)\s*?$",str(value)):         
                buffer = []
                #ret = []
                # reg vyraz pro rozdelini retezce podle vice znaku
                tmp = re.split("\(|\)",value)
                for i in tmp[:-1]:
                    if "," in i:
                        buffer.append(i.split(","))
                    else:
                        buffer.append([i])
                for i in product(*buffer):
                    ret.append(''.join(i))
                print("return True, nazev a range")
                return ret#, True

            #pokud se jedna pouze o sekvenci, tak vraci seznam
            elif "," in str(value):
                print("return False, sekvence")
                return value.split(",")#, False

            #pokud nevyhovuje ani jeden vzor, tak vrati original
            else:
                print("return False, nic")
                return value#, False
        except AttributeError:
            print("return False, jinej datovej typ")
            return value, False
    
            

    def _rekurze(self, data, group, class_, method, subMethod,groupNum,idNum):
        groupLevel = group # flag, ktery rika jestli mam odpojovat skupinu
        groupNumber = groupNum # pocet prvku skupiny, pro odebirani
        class_ = class_ # flag, ktery rika jestli vyskakuju ze tridy
        method = method # flag, ktery rika jeslti vyskakuju z metody
        subMethod = subMethod # flag, ktery mi rika jestli vyskakuju z podmetody
        #idNum promena, ktera obsahuje identifikator rozhrani
        #mohl bych ji sem taky pro prehlednost pridat

        #flag = None 
        
        for i in data:
            #print("prvni prvek z foru:", i)
            input("stiskni enter")
            try:
                if type(i) == type(str()):
                    #print("dosel jsem ke konci")
                    if type(data[i]) == type(dict()):
                        if self.subMethodName == "":
                            self.subMethodName = self.methodName+"_"+str(i)
                        else:
                            self.subMethodName = self.subMethodName+"_"+str(i)
                        print("nasel jse m submethod",self.subMethodName)
                        self._rekurze(data[i],False,False,False,True,groupNumber,None)
                    data[i] = self._unpack(data[i])
                    #if flag == None:
                    #    flag = flag2
                    #else:
                    #    if flag != flag2:
                    #        print("Disallowed parameters.")
                    #        exit(1)
                    print("klic:",i," hodnota:",data[i])
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
                    self._rekurze(i["group"],True,False,False,False,groupNumber,None) 
                else:
                    if self.className == "":
                        self.className = list(i.keys())[0]
                        #print("nasel jsem tridu",self.className ," dalsi kolo:",i[self.className])
                        print("nasel jsem tridu",self.className)
                        input("stiskni enter")
                        #class_ = True
                        #idNum = self._checkId(self.className)
                        #print("checkId vratilo", idNum)
                        self._rekurze(i[self.className],False,True,False,False,groupNumber,None)

                    elif self.methodName == "":
                        self.methodName = list(i.keys())[0]
                        #print("nasel jsem metodu",self.methodName," dalsi kolo:",i[self.methodName])
                        print("nasel jsem metodu",self.methodName)
                        input("stiskni enter")
                        idNum,name,index = self._checkId(self.methodName)
                        print("checkId vratilo", idNum, type(idNum))
                        #kontroluju zda byl nalezen identifikator
                        #pak ho tam musim zase pridat, aby se nasel spravny klic
                        if idNum:
                            #if type(idNum) == type(list()):
                            #    num = "("+str(idNum[0])+","+str(idNum[1])+","+str(idNum[2])+")"
                            #else:
                            #    num = str(idNum)
                            self.methodName = name
                            self._rekurze(i[self.methodName+index],False,False,True,False,groupNumber,idNum)
                        else:
                            self._rekurze(i[self.methodName],False,False,True,False,groupNumber,idNum)
                            
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
            print("identifikator: ",idNum)
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
            
            
class orchestrate():
    pass                 
 
