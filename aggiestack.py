from rack import *

class CloudManager:
    RackDict ={} # Stores info about all the active racks
    InstDict ={} # Stores info about which instance is running on which rack
    
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
                retVal = rack.showImgData()
                if retVal != "SUCCESS":
                    print "Error in displaying info for rack "+key
        return "SUCCESS"

# Function to show remaining Hdwr resources
    def showRemHdwr(self):
        retVal = "FAILURE"
        for name,rack in CloudManager.RackDict.iteritems():
            retVal = rack.showRemInfo()
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
            retVal = rack.showInstanceInfo()
            if(retVal != "SUCCESS"):
                break
        return retVal

# Function to show on which Hdwr and rack each instance is running on
    def showHdwrInst(self):
        retVal = "FAILURE"
        if len(CloudManager.InstDict) == 0:
            print "No instances running"
            return "FAILURE"
        for name,rack in CloudManager.RackDict.iteritems():
            retVal = rack.showHdwrInfo()
            if(retVal != "SUCCESS"):
                break
        return retVal

# Function to create a new instace on this rack
# priority to rack where image is pre-cached
    def createInst(self,imageName, flavorName, instName):
        return "SUCCESS"

# Function to delete an existing instance
    def deleteInst(self,instName):
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
    
