import sys
import os
import copy

CONFIG_TYPES = ["HDWR","IMAGE","FLAVOR"]

# Stores information about a single hardware config
class HdwrConfig:
    def __init__(self, name, rackName, ip, mem, numDisks, numCores):
        self.name = name
        self.rackName = rackName
        self.ip = ip
        self.mem = int(mem)
        self.numDisks = int(numDisks)
        self.numCores = int(numCores)
        self.remMem = int(mem)
        self.remDisks = int(numDisks)
        self.remCores = int(numCores)
    def showConfig(self):
        infoStr = "Name:-> "+self.name+" RackName:-> "+self.rackName+" IP:-> "\
        +self.ip+" Mem:-> "+str(self.mem)+" NumDisks:-> "+str(self.numDisks)+\
        " NumCores:-> "+str(self.numCores)
        print(infoStr)
    def showRemInfo(self):
        infoStr = "Hdwr "+self.name+" on rack "+self.rackName+" has mem:-> "+\
        str(self.remMem)+" disks:-> "+str(self.remDisks)+" cores:-> "+\
        str(self.remCores)+" remaining"
        print(infoStr)

# Stores static information about a single Image config
class ImageConfig:
    def __init__(self,name,size,path):
        self.name = name
        self.size = int(size)
        self.path = path
    def showConfig(self):
        infoStr = "Name:-> "+self.name+" Size:-> "+ str(self.size)+" Path:-> "\
        + self.path
        print(infoStr)

# Stores static information about a single Flavor config
class FlavorConfig:
    def __init__(self,name,mem,numDisks,numVCpus):
        self.name = name
        self.mem = int(mem)
        self.numDisks = int(numDisks)
        self.numVCpus = int(numVCpus)
    def showConfig(self):
        infoStr = "Name:-> "+self.name+" Mem:-> "+str(self.mem)+" NumDisks:-> "+\
        str(self.numDisks)+" NumVCpus:-> "+str(self.numVCpus)
        print(infoStr)

# stores information about a single instance
class Instance:
    def __init__(self,instName,rackName,flavorName,imageName,hdwrName):
        self.instName = instName
        self.rackName = rackName
        self.flavorName = flavorName
        self.imageName = imageName
        self.hdwrName = hdwrName
    def showInstanceInfo(self):
        infoStr = "InstName:-> "+self.instName+" FlavorName:-> "+self.flavorName+\
        " ImageName: "+self.imageName
        print(infoStr)
    def showHdwrInfo(self):
        infoStr = "Instance "+self.instName+" is running on hdwr-> "+ self.hdwrName+\
        " on the rack:-> "+self.rackName
        print(infoStr)

# Rack Manager class:contians functions to manage the servers on the racks
# load/delete/show instance information.

class RackManager:

# Store all configuration data as dicts with name as key and object as value
    ImageConfigDict = {}
    FlavorConfigDict= {}
    def __init__(self,name,capacity):
        self.name = name
        self.capacity = int(capacity)
        self.remCapacity = int(capacity) # Image cache capacity
        self.hdwrConfigDict = {}
        self.instanceDict = {} # Store info about all instances on the rack
        self.currLoadList = [] # Stores info about total load on the rack
        self.imgCacheList = [] # Stores info about the image caches on the rack

# Function to add a new hdwr to the rack
    def addHdwr(self,info):
        if info[0] in self.hdwrConfigDict:
            print ("Hdwr "+info[0]+" already exists")
            return "FAILURE"
        self.hdwrConfigDict[info[0]] = HdwrConfig(info[0],info[1],info[2],\
        info[3],info[4],info[5])
        self.currLoadList.append([info[0],0])
        return "SUCCESS"

# Function to remove hdwr from activley hosting new instances
    def removeHdwr(self,name):
        
        if name not in self.hdwrConfigDict:
            return "FAILURE"
        for tup in self.currLoadList:
            if name == tup[0]:
                self.currLoadList.remove(tup)
                break
        if name in self.hdwrConfigDict:
            del self.hdwrConfigDict[name]
        return "SUCCESS"
    
        
# Static functions to copy the required configuration data
    @staticmethod
    def copyImageConfigDict(imageDict):
        RackManager.ImageConfigDict = copy.deepcopy(imageDict)
    
    @staticmethod
    def copyFlavorConfigDict(flavorDict):
        RackManager.FlavorConfigDict = copy.deepcopy(flavorDict)

# Function to show hardware on the rack
    def showConfigData(self):
        configDict = self.hdwrConfigDict
        if len(configDict) == 0:
            print "Hdwr Configuration was not loaded on rack "+self.name
            return "FAILURE"
        for name,config in configDict.iteritems():
            config.showConfig()
        return "SUCCESS"

# Function to show cached images on the rack
    def showImgData(self):
      if len(self.imgCacheList) == 0:
          print "ImgCacheList empty on rack "+self.name
          return "Failure"
      for img in self.imgCacheList:
          print "RackName:-> "+self.name+" has image ImgName:-> "+img
      return "Success"

# Function to show remaining Hdwr resources
    def showRemHdwr(self):
        if len(self.hdwrConfigDict) == 0:
            print "Hdwr Configuration was not loaded on rack "+self.name
            return "FAILURE"
        for name,config in self.hdwrConfigDict.iteritems():
            config.showRemInfo()
        return "SUCCESS"
        
# Function to list all info about the instances running
    def showInstances(self):
        if len(self.instanceDict) == 0:
            print "No instances running on rack "+self.name
            return "FAILURE"
        for name,config in self.instanceDict.iteritems():
            config.showInstanceInfo()
        return "SUCCESS"

# Function to check if there is image in the cache
    def isImageInCache(self,imgName):
        return imgName in self.imgCacheList

# Function to add image to the cache. Uses LIFO eviction scheme
    def addImgToCache(self,imgName):
        if RackManager.ImageConfigDict[imgName].size <= self.remCapacity:
            self.remCapacity -= RackManager.ImageConfigDict[imgName].size
            self.imgCacheList.append(imgName)
        else:
            while RackManager.ImageConfigDict[imgName].size > self.remCapacity:
                img = self.imgCacheList.pop()
                self.remCapacity += RackManager.ImageConfigDict[img].size
            self.remCapacity -= RackManager.ImageConfigDict[imgName].size
            self.imgCacheList.append(imgName)

# Fuction to check if an instance can be created with a given flavor
    def isInstCreatable(self,flavorName):
        
        self.currLoadList.sort(key=lambda tup:tup[1])
        for tup in self.currLoadList:
            if (self.hdwrConfigDict[tup[0]].remCores >= \
                   RackManager.FlavorConfigDict[flavorName].numVCpus) and\
                (self.hdwrConfigDict[tup[0]].remMem >= \
                   RackManager.FlavorConfigDict[flavorName].mem) and\
                (self.hdwrConfigDict[tup[0]].remDisks >= \
                   RackManager.FlavorConfigDict[flavorName].numDisks):
                       return True
        return False
            
# Function to show on which Hdwr each instance is running on
    def showHdwrInst(self):
        if len(self.instanceDict) == 0:
            print "No instances running on rack "+self.name
            return "FAILURE"
        for name,config in self.instanceDict.iteritems():
            config.showHdwrInfo()
        return "SUCCESS"
        
# Function to create a new instace on this rack
# Using least connection method for load balancing
    def createInst(self,imageName, flavorName, instName):
        # Find appropiate server for the instance
        self.currLoadList.sort(key=lambda tup:tup[1])
        for tup in self.currLoadList:
            if (self.hdwrConfigDict[tup[0]].remCores >= \
                   RackManager.FlavorConfigDict[flavorName].numVCpus) and\
                (self.hdwrConfigDict[tup[0]].remMem >= \
                   RackManager.FlavorConfigDict[flavorName].mem) and\
                (self.hdwrConfigDict[tup[0]].remDisks >= \
                   RackManager.FlavorConfigDict[flavorName].numDisks):
                       tup[1]+=1
                       # create a new instance object
                       self.instanceDict[instName] = Instance(instName,\
                       self.name,flavorName,imageName,tup[0])
                       # Update resource stats of the server
                       self.hdwrConfigDict[tup[0]].remCores -=\
                       RackManager.FlavorConfigDict[flavorName].numVCpus
                       self.hdwrConfigDict[tup[0]].remMem -=\
                       RackManager.FlavorConfigDict[flavorName].mem
                       self.hdwrConfigDict[tup[0]].remDisks -=\
                       RackManager.FlavorConfigDict[flavorName].numDisks
                       break
                       
# Function to delete an existing instance on this rack
    def deleteInst(self,instName):
        if instName not in self.instanceDict:
            print(instName+" does not exist")
            return "FAILURE"
        hdwrName = self.instanceDict[instName].hdwrName
        flavorName = self.instanceDict[instName].flavorName
        
        # update the resource stats on the hardware
        self.hdwrConfigDict[hdwrName].remCores +=\
        RackManager.FlavorConfigDict[flavorName].numVCpus
        self.hdwrConfigDict[hdwrName].remMem +=\
        RackManager.FlavorConfigDict[flavorName].mem
        self.hdwrConfigDict[hdwrName].remDisks +=\
        RackManager.FlavorConfigDict[flavorName].numDisks
        
        # Update loadbalancer list
        for tup in self.currLoadList:
            if tup[0] == hdwrName:
                tup[1]-=1
                break
        # delete the instance entry
        del self.instanceDict[instName]
        return "SUCCESS"