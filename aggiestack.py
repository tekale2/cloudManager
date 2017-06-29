import sys
import os

CONFIG_TYPES = ["HDWR","IMAGE","FLAVOR"]

# Stores information about a single hardware config
class HdwrConfig:
    def __init__(self, name, ip, mem, numDisks, numCores):
        self.name = name
        self.ip = ip
        self.mem = int(mem)
        self.numDisks = int(numDisks)
        self.numCores = int(numCores)
        self.remMem = int(mem)
        self.remDisks = int(numDisks)
        self.remCores = int(numCores)
    def showConfig(self):
        infoStr = "Name:-> "+self.name+" IP:-> "+self.ip+" Mem:-> "+str(self.mem)+\
        " NumDisks:-> "+str(self.numDisks)+" NumCores:-> "+str(self.numCores)
        print(infoStr)
    def showRemInfo(self):
        infoStr = "Hdwr "+self.name+" has mem:-> "+str(self.remMem)+" disks:-> "+\
        str(self.remDisks)+" cores:-> "+str(self.remCores)+" remaining"
        print(infoStr)

# Stores static information about a single Image config
class ImageConfig:
    def __init__(self,name,path):
        self.name = name
        self.path = path
    def showConfig(self):
        infoStr = "Name:-> "+self.name+" Path:-> "+ self.path
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
    def __init__(self,instName,flavorName,imageName,hdwrName):
        self.instName = instName
        self.flavorName = flavorName
        self.imageName = imageName
        self.hdwrName = hdwrName
    def showInstanceInfo(self):
        infoStr = "InstName:-> "+self.instName+" FlavorName:-> "+self.flavorName+\
        " ImageName: "+self.imageName
        print(infoStr)
    def showHdwrInfo(self):
        infoStr = "Instance "+self.instName+" is running on "+ self.hdwrName
        print(infoStr)

# Cloud Manager class:contians functions to load/show configs and
# load/delete/show instance information.

class CloudManager:

# Store all configuration data as dicts with name as key and object as value
    HdwrConfigDict = {} 
    ImageConfigDict = {}
    FlavorConfigDict= {}
    InstanceDict  = {}  # Store info about all instances
    CurrLoadList = []   # stores number of instances in a physical sever. Used
                        # load balancing

# Function to load the configuration data from the file
    def loadConfigData(self, filename, configType):
        if os.path.exists(filename):
            with open(filename , 'r') as f:
                configSize = int(f.readline())
                for line in f:
                    info = [str(x) for x in line.strip().split()]
                    if configType == CONFIG_TYPES[0]:
                        CloudManager.HdwrConfigDict[info[0]] = HdwrConfig(info[0],\
                                                    info[1],info[2],info[3],info[4])
                        CloudManager.CurrLoadList.append([info[0],0])
                    elif configType == CONFIG_TYPES[1]:
                        CloudManager.ImageConfigDict[info[0]] = ImageConfig(info[0],\
                                                              info[1])
                    else:
                        CloudManager.FlavorConfigDict[info[0]] = FlavorConfig(info[0]\
                                                           ,info[1],info[2],info[3])
            return "SUCCESS"
        else:
            print "File "+filename+" does not exist"
            return "FAILURE"

# Function to show the configuration data
    def showConfigData(self, configType):
        configDict = None
        if configType == CONFIG_TYPES[0]:
            configDict = CloudManager. HdwrConfigDict
        elif configType == CONFIG_TYPES[1]:
            configDict = CloudManager.ImageConfigDict
        else:
            configDict = CloudManager.FlavorConfigDict
        if len(configDict) == 0:
            print "Configuration was not loaded"
            return "FAILURE"
        for name,config in configDict.iteritems():
            config.showConfig()
        return "SUCCESS"

# Function to show remaining Hdwr resources
    def showRemHdwr(self):
        if len(CloudManager.HdwrConfigDict) == 0:
            print "Hdwr Configuration was not loaded"
            return "FAILURE"
        for name,config in CloudManager.HdwrConfigDict.iteritems():
            config.showRemInfo()
        return "SUCCESS"
        
# Function to list all info about the instances running
    def showInstances(self):
        if len(CloudManager.InstanceDict) == 0:
            print "No instances running"
            return "FAILURE"
        for name,config in CloudManager.InstanceDict.iteritems():
            config.showInstanceInfo()
        return "SUCCESS"

# Function to show on which Hdwr each instance is running on
    def showHdwrInst(self):
        if len(CloudManager.InstanceDict) == 0:
            print "No instances running"
            return "FAILURE"
        for name,config in CloudManager.InstanceDict.iteritems():
            config.showHdwrInfo()
        return "SUCCESS"
        
# Function to create a new instace
# Using least connection method for load balancing
    def createInst(self,imageName, flavorName, instName):
        if instName in CloudManager.InstanceDict:
            print(instName+" already exists")
            return "FAILURE"
        elif flavorName not in CloudManager.FlavorConfigDict:
            print("Invalid flavorName "+flavorName)
            return "FAILURE"
        elif imageName not in CloudManager.ImageConfigDict:
            print("Invalid imageName "+imageName)
            return "FAILURE"
        # Find appropiate server for the instance
        CloudManager.CurrLoadList.sort(key=lambda tup:tup[1])
        for tup in CloudManager.CurrLoadList:
            if (CloudManager.HdwrConfigDict[tup[0]].remCores >= \
                   CloudManager.FlavorConfigDict[flavorName].numVCpus) and\
                (CloudManager.HdwrConfigDict[tup[0]].remMem >= \
                   CloudManager.FlavorConfigDict[flavorName].mem) and\
                (CloudManager.HdwrConfigDict[tup[0]].remDisks >= \
                   CloudManager.FlavorConfigDict[flavorName].numDisks):
                       tup[1]+=1
                       # create a new instance object
                       CloudManager.InstanceDict[instName] = Instance(instName,\
                       flavorName,imageName,tup[0])
                       # Update resource stats of the server
                       CloudManager.HdwrConfigDict[tup[0]].remCores -=\
                       CloudManager.FlavorConfigDict[flavorName].numVCpus
                       CloudManager.HdwrConfigDict[tup[0]].remMem -=\
                       CloudManager.FlavorConfigDict[flavorName].mem
                       CloudManager.HdwrConfigDict[tup[0]].remDisks -=\
                       CloudManager.FlavorConfigDict[flavorName].numDisks
                       
                       return "SUCCESS"
        print("Resoucres exhausted, Instance "+instName+" cannot be created")
        return "FAILURE"
                       
# Function to delete an existing instance
    def deleteInst(self,instName):
        if instName not in CloudManager.InstanceDict:
            print(instName+" does not exist")
            return "FAILURE"
        hdwrName = CloudManager.InstanceDict[instName].hdwrName
        flavorName = CloudManager.InstanceDict[instName].flavorName
        
        # update the resource stats on the hardware
        CloudManager.HdwrConfigDict[hdwrName].remCores +=\
        CloudManager.FlavorConfigDict[flavorName].numVCpus
        CloudManager.HdwrConfigDict[hdwrName].remMem +=\
        CloudManager.FlavorConfigDict[flavorName].mem
        CloudManager.HdwrConfigDict[hdwrName].remDisks +=\
        CloudManager.FlavorConfigDict[flavorName].numDisks
        
        # Update loadbalancer list
        for tup in CloudManager.CurrLoadList:
            if tup[0] == hdwrName:
                tup[1]-=1
                break
        # delete the instance entry
        del CloudManager.InstanceDict[instName]
        return "SUCCESS"


# reads the input file and executes the commands
def execCommands():
    cloudManager = CloudManager()
    inputFile = sys.argv[1]
    outfile = open("output.log","w")
    retVal =""
    if os.path.exists(inputFile):
        with open(inputFile,'r') as f:
            for line in f:
                params = [x for x in line.strip().split()]
                if len(params)<3:
                    continue
    # Parse the commands and execute them accordingly
                if params[1].lower() == "config":
                    if params[2].lower() == "--hardware":
                        retVal = cloudManager.loadConfigData(params[3],CONFIG_TYPES[0])
                    elif params[2].lower() == "--images":
                        retVal = cloudManager.loadConfigData(params[3],CONFIG_TYPES[1])
                    elif params[2].lower() == "--flavors":
                        retVal = cloudManager.loadConfigData(params[3],CONFIG_TYPES[2])
                    else:
                        print("Invalid command")
                        continue
                    outfile.write(line.strip()+ " <"+retVal+">\n")
        
                elif params[1].lower() == "show":
                    if params[2].lower() == "hardware":
                        retVal = cloudManager.showConfigData(CONFIG_TYPES[0])
                    elif params[2].lower() == "images":
                        retVal = cloudManager.showConfigData(CONFIG_TYPES[1])
                    elif params[2].lower() == "flavors":
                        retVal = cloudManager.showConfigData(CONFIG_TYPES[2])
                    else:
                        print("Invalid command")
                        continue
                    outfile.write(line.strip()+ " <"+retVal+">\n")
    
                elif params[1].lower() == "server":
                    if params[2].lower() == "list":
                       retVal = cloudManager.showInstances()
                    elif params[2].lower() == "delete":
                        retVal = cloudManager.deleteInst(params[3])
                    elif params[2].lower() == "create":
                        instName =""
                        flavorName =""
                        imageName =""
                        for i in range(3,len(params)):
                            if params[i].lower() == "--image":
                                imageName = params[i+1]
                                i+=1
                            elif params[i].lower() == "--flavor":
                                flavorName = params[i+1]
                                i+=1
                            else:
                                instName = params[i]
                        retVal = cloudManager.createInst(imageName,flavorName,instName)
                    else:
                        print("Invalid command")
                        continue
                    outfile.write(line.strip()+ " <"+retVal+">\n")
                        
                elif params[1].lower() == "admin":
                    if params[2].lower() == "show" and params[3].lower() == "hardware":
                        retVal = cloudManager.showRemHdwr()
                    elif params[2].lower() == "show" and params[3].lower() == "instances":
                        retVal = cloudManager.showHdwrInst()
                    else:
                        print("Invalid command")
                        continue
                    outfile.write(line.strip()+ " <"+retVal+">\n")
    else:
        print("File "+inputFile+" does not exist")
    outfile.close()

if __name__ == "__main__":
    execCommands()
    
