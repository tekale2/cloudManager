from rack import *

class CloudManager:
    RackDict ={} # Stores info about all the active racks
    InstDict ={} # Stores info about which instance is running on which rack
    RackList =[] # stores rackNames in sorted order of remaining capacity
    # Store all configuration data as dicts with name as key and object as value
    ImageConfigDict = {}
    FlavorConfigDict= {}

# Function to load the configuration data from the file
    def loadConfigData(self, filename, configType):
        if os.path.exists(filename):
            with open(filename , 'r') as f:
                configSize = int(f.readline())
                for line in f:
                    info = [str(x) for x in line.strip().split()]
                    if configType == CONFIG_TYPES[0]:
                        if configSize >0:
                            CloudManager.RackDict[info[0]] = RackManager(info[0],info[1])
                            CloudManager.RackList.append(info[0])
                            configSize-=1
                        elif configSize == 0:
                            configSize-=1
                            continue
                        else:
                            CloudManager.RackDict[info[1]].addHdwr(info)
                            
                    elif configType == CONFIG_TYPES[1]:
                        CloudManager.ImageConfigDict[info[0]] = ImageConfig(info[0],\
                                                              info[1],info[2])
                    else:
                        CloudManager.FlavorConfigDict[info[0]] = FlavorConfig(info[0]\
                                                           ,info[1],info[2],info[3])
            if configType == CONFIG_TYPES[1]:
                RackManager.copyImageConfigDict(CloudManager.ImageConfigDict)
            elif configType == CONFIG_TYPES[2]:
                RackManager.copyFlavorConfigDict(CloudManager.FlavorConfigDict)
            return "SUCCESS"
        else:
            print "File "+filename+" does not exist"
            return "FAILURE"

# Function to add new machine to specified rack
    def addNewHdwr(self, mem,disks,vcpus,ip,hdwrName,rackName):
        if (mem == "" or disks == "" or vcpus =="" or ip=="" or hdwrName ==""):
            print("Invalid add new machine command")
            return "FAILURE"
        if rackName not in CloudManager.RackDict:
            print("Invalid rack name")
            return "FAILURE"
        info = [hdwrName,rackName,ip,mem,disks,vcpus]
        return CloudManager.RackDict[rackName].addHdwr(info)

# Function to remove hardware from the datacenter
    def removeHdwr(self,hdwrName):
        retVal = "FAILURE"
        for name,rack in CloudManager.RackDict.iteritems():
            retVal = rack.removeHdwr(hdwrName)
            if retVal == "SUCCESS":
                break
        return retVal

# Function to evacuate the rack with rack name
# For this project instances running on that rack would be
# created on  other machines and this rack would be removed

    def evacuateRack(self,rackName):
        if rackName not in CloudManager.RackDict:
            return "FAILURE"
        instList =[]
        # remove rack from the racklist to avoid creation of new instances
        CloudManager.RackList.remove(rackName)
        for inst,rack in CloudManager.InstDict.iteritems():
            if rack == rackName:
                instList.append(inst)
        evcuatedCount = 0
        
        # spwan the instaces on new hdwr
        for inst in instList:
            imageName =\
            CloudManager.RackDict[rackName].instanceDict[inst].imageName
            flavorName =\
            CloudManager.RackDict[rackName].instanceDict[inst].flavorName
            del CloudManager.InstDict[inst]
            retVal = self.createInst(imageName, flavorName, inst)
            if retVal == "SUCCESS":
                evcuatedCount+=1
                CloudManager.RackDict[rackName].deleteInst(inst)
            else:
                CloudManager.InstDict[inst] = rackName
        if evcuatedCount == len(instList):
            return "SUCCESS"
        else:
            "Not all instances running on th rack "+rackName+" were evacuated"
            return "FAILURE"

# Function to show the configuration data
    def showConfigData(self, configType):
        configDict = None
        if configType == CONFIG_TYPES[0]:
            for key,rack in CloudManager.RackDict.iteritems():
                retVal = rack.showConfigData()
                if retVal != "SUCCESS":
                    print "Error in displaying info for rack "+key
            return "SUCCESS"
        elif configType == CONFIG_TYPES[1]:
            configDict = CloudManager.ImageConfigDict
        else:
            configDict = CloudManager.FlavorConfigDict
        if len(configDict) == 0:
            print "Configuration was not loaded"
            return "FAILURE"
        for name,config in configDict.iteritems():
            config.showConfig()
        if configType == CONFIG_TYPES[1]:
            for key,rack in CloudManager.RackDict.iteritems():
                rack.showImgData()
        return "SUCCESS"

# Function to show remaining Hdwr resources
    def showRemHdwr(self):
        retVal = "FAILURE"
        for name,rack in CloudManager.RackDict.iteritems():
            retVal = rack.showRemHdwr()
            if(retVal != "SUCCESS"):
                break
        return retVal
        
# Function to list all info about the instances running
    def showInstances(self):
        retVal = "FAILURE"
        if len(CloudManager.InstDict) == 0:
            print "No instances running"
            return "FAILURE"
        for name,rack in CloudManager.RackDict.iteritems():
            retVal = rack.showInstances()
            if(retVal != "SUCCESS"):
                break
        return retVal

# Function to show on which Hdwr and rack each instance is running on
    def showHdwrInst(self):
        if len(CloudManager.InstDict) == 0:
            print "No instances running on any rack"
            return "SUCCESS"
        for name,rack in CloudManager.RackDict.iteritems():
            rack.showHdwrInst()
        return "SUCCESS"

# Function to show image caches on a given rack
    def showImgcaches(self,rackName):
        if rackName not in CloudManager.RackDict:
            print (rackName+" does not exist")
            return "FAILURE"
        CloudManager.RackDict[rackName].showImgData()
        print("rack "+rackName+" has mem:-> " +\
        str(CloudManager.RackDict[rackName].remCapacity)+" remaining")
        return "SUCCESS"
        

# Function to create a new instace on this rack
# priority to rack where image is pre-cached
    def createInst(self,imageName, flavorName, instName):
        if instName in CloudManager.InstDict:
            print(instName+" already exists")
            return "FAILURE"
        elif flavorName not in CloudManager.FlavorConfigDict:
            print("Invalid flavorName "+flavorName)
            return "FAILURE"
        elif imageName not in CloudManager.ImageConfigDict:
            print("Invalid imageName "+imageName)
            return "FAILURE"
        firstPrior = None
        createImg  = True

# proirtize placement of inst on cache with image else with maximumrem capacity
        CloudManager.RackList.sort(key=lambda x:CloudManager.RackDict[x].remCapacity\
        ,reverse=True)
        for rackName in CloudManager.RackList:
            if CloudManager.RackDict[rackName].isInstCreatable(flavorName):
                if firstPrior == None:
                    firstPrior = rackName
                if CloudManager.RackDict[rackName].isImageInCache(imageName):
                    firstPrior = rackName
                    createImg = False
                    break
        if firstPrior == None:
            print("Resoucres exhausted, Instance "+instName+" cannot be created")
            return "FAILURE"

        # Create the instance on the rack "firstPrior"
        CloudManager.InstDict[instName] = firstPrior
        if createImg:
            CloudManager.RackDict[firstPrior].addImgToCache(imageName)
        CloudManager.RackDict[firstPrior].createInst(imageName, flavorName, instName)
        return "SUCCESS"

# Function to delete an existing instance
    def deleteInst(self,instName):
        if instName not in CloudManager.InstDict:
            print (instName +" does not exists")
            return "FAILURE"
        rackName = CloudManager.InstDict[instName]
        del CloudManager.InstDict[instName]
        return CloudManager.RackDict[rackName].deleteInst(instName)


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
                    elif params[2].lower() == "show" and (params[3].lower() ==\
                    "imagecaches" or params[3].lower() == "imagecaches"):
                        retVal = cloudManager.showImgcaches(params[4])
                    elif params[2].lower() == "remove":
                        retVal = cloudManager.removeHdwr(params[3])
                    elif params[2].lower() == "evacuate":
                        retVal = cloudManager.evacuateRack(params[3])
                    elif params[2].lower() == "add":
                        mem   = ""
                        disks = ""
                        vcpus = ""
                        ip    = ""
                        rackName  = ""
                        hdwrName = ""
                        for i in range(3,len(params)):
                            if params[i].lower() == "--mem":
                                mem = params[i+1]
                                i+=1
                            elif params[i].lower() == "--disk":
                                disks = params[i+1]
                                i+=1
                            elif params[i].lower() == "--rack":
                                rackName = params[i+1]
                                i+=1
                            elif params[i].lower() == "--vcpus":
                                vcpus = params[i+1]
                                i+=1
                            elif params[i].lower() == "--ip":
                                ip = params[i+1]
                                i+=1
                            else:
                                hdwrName = params[i]
                        retVal = cloudManager.addNewHdwr(mem,disks,vcpus,ip,\
                        hdwrName,rackName)                        
                    else:
                        print("Invalid command")
                        continue
                    outfile.write(line.strip()+ " <"+retVal+">\n")
    else:
        print("File "+inputFile+" does not exist")
    outfile.close()

if __name__ == "__main__":
    execCommands()
    
