import sys

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
        infoStr = "Name: "+self.name+" IP: "+self.ip+" Mem: "+str(self.mem)+\
        " NumDisks: "+str(self.numDisks)+" NumCores "+str(self.numCores)
        print(infoStr)
    def showRemInfo(self):
        infoStr = "Hdwr "+self.name+" has mem: "+str(self.remMem)+" disks: "+\
        str(self.remDisks)+" cores: "+str(self.remCores)+" remaining"
        print(infoStr)

# Stores static information about a single Image config
class ImageConfig:
    def __init__(self,name,path):
        self.name = name
        self.path = path
    def showConfig(self):
        infoStr = "Name: "+self.name+" Path: "+ self.path
        print(infoStr)

# Stores static information about a single Flavor config
class FlavorConfig:
    def __init__(self,name,mem,numDisks,numVCpus):
        self.name = name
        self.mem = int(mem)
        self.numDisks = int(numDisks)
        self.numVCpus = int(numVCpus)
    def showConfig(self):
        infoStr = "Name: "+self.name+" Mem: "+str(self.mem)+" NumDisks: "+\
        str(self.numDisks)+" NumVCpus: "+str(self.numVCpus)
        print(infoStr)

# stores information about a single instance
class Instance:
    def __init__(self,instName,flavorName,imageName,hdwrName):
        self.instName = instName
        self.flavorName = flavorName
        self.imageName = imageName
        self.hdwrName = hdwrName
    def showInstanceInfo(self):
        infoStr = "InstName: "+self.instName+" FlavorName: "+self.flavorName+\
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
        with open(filename , 'r') as f:
            configSize = int(f.readline())
            for line in f:
                info = [str(x) for x in line.split()]
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
        return "Successfully loaded configuration from "+filename

# Function to show the configuration data
    def showConfigData(self, configType):
        configDict = None
        if configType == CONFIG_TYPES[0]:
            configDict = CloudManager. HdwrConfigDict
        elif configType == CONFIG_TYPES[1]:
            configDict = CloudManager.ImageConfigDict
        else:
            configDict = CloudManager.FlavorConfigDict
        for name,config in configDict.iteritems():
            config.showConfig()

# Function to show remaining Hdwr resources
    def showRemHdwr(self):
        for name,config in CloudManager.HdwrConfigDict.iteritems():
            config.showRemInfo()
        
# Function to list all info about the instances running
    def showInstances(self):
        for name,config in CloudManager.InstanceDict.iteritems():
            config.showInstanceInfo()

# Function to show on which Hdwr each instance is running on
    def showHdwrInst(self):
        for name,config in CloudManager.InstanceDict.iteritems():
            config.showHdwrInfo()
        
# Function to create a new instace
# Using least connection method for load balancing
    def createInst(self,imageName, flavorName, instName):
        if instName in CloudManager.InstanceDict:
            return instName+" already exists"
        elif flavorName not in CloudManager.FlavorConfigDict:
            return "Invalid flavorName "+flavorName
        elif imageName not in CloudManager.ImageConfigDict:
            return "Invalid imageName "+imageName
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
                       
                       return "Successfully created instance "+instName
        return "Resoucres exhausted, Instance "+instName+" cannot be created"
                       
# Function to delete an existing instance
    def deleteInst(self,instName):
        if instName not in CloudManager.InstanceDict:
            return instName+" does not exist"
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
        return "Successfully deleted Instance "+instName


# reads the input file and executes the commands
def execCommands():
    cloudManager = CloudManager()
    inputFile = sys.argv[1]
    msg =""
    with open(inputFile,'r') as f:
        for line in f:
            params = [x for x in line.split()]
            if len(params)<3:
                continue
# Parse the commands and execute them accordingly
            if params[1].lower() == "config":
                if params[2].lower() == "--hardware":
                    msg = cloudManager.loadConfigData(params[3],CONFIG_TYPES[0])
                elif params[2].lower() == "--images":
                    msg = cloudManager.loadConfigData(params[3],CONFIG_TYPES[1])
                elif params[2].lower() == "--flavors":
                    msg = cloudManager.loadConfigData(params[3],CONFIG_TYPES[2])
                print(msg)
                
            elif params[1].lower() == "show":
                if params[2].lower() == "hardware":
                    cloudManager.showConfigData(CONFIG_TYPES[0])
                elif params[2].lower() == "images":
                    cloudManager.showConfigData(CONFIG_TYPES[1])
                elif params[2].lower() == "flavors":
                    cloudManager.showConfigData(CONFIG_TYPES[2])

            elif params[1].lower() == "server":
                if params[2].lower() == "list":
                    cloudManager.showInstances()
                elif params[2].lower() == "delete":
                    msg = cloudManager.deleteInst(params[3])
                    print(msg)
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
                    msg = cloudManager.createInst(imageName,flavorName,instName)
                    print(msg)
                    
            elif params[1].lower() == "admin":
                if params[2].lower() == "show" and params[3].lower() == "hardware":
                    cloudManager.showRemHdwr()
                elif params[2].lower() == "show" and params[3].lower() == "instances":
                    cloudManager.showHdwrInst()

if __name__ == "__main__":
    execCommands()
    
