import sys

CONFIG_TYPES = ["HDWR","IMAGE","FLAVOR"]
# Stores static information about a single hardware config
class HdwrConfig:
    def __init__(self, name, ip, mem, numDisks, numCores):
        self.name = name
        self.ip = ip
        self.mem = int(mem)
        self.numDisks = int(numDisks)
        self.numCores = int(numCores)
    def showConfig(self):
        infoStr = "Name: "+self.name+" IP: "+self.ip+" Mem: "+str(self.mem)+\
        " NumDisks: "+str(self.numDisks)+" NumCores "+str(self.numCores)
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

# Config class to store all the configuration data
class ConfigData:
    HdwrConfigList = []
    ImageConfigList = []
    FlavorConfigList = []
    r=10
# Function tp load the configuration data
    def loadConfigData(self, filename, configType):
        configSize = 0
        with open(filename , 'r') as f:
            configSize = int(f.readline())
            for line in f:
                info = [str(x) for x in line.split()]
                if configType == CONFIG_TYPES[0]:
                    ConfigData.HdwrConfigList.append(HdwrConfig(info[0],info[1],info[2],\
                    info[3],info[4]))
                elif configType == CONFIG_TYPES[1]:
                    ConfigData.ImageConfigList.append(ImageConfig(info[0],info[1]))
                else:
                    ConfigData.FlavorConfigList.append(FlavorConfig(info[0],info[1],\
                    info[2],info[3]))
        print("Successfully loaded configuration from "+filename)

# Function to show the configuration data
    def showConfigData(self, configType):
        configList = None
        if configType == CONFIG_TYPES[0]:
            configList = ConfigData. HdwrConfigList
        elif configType == CONFIG_TYPES[1]:
            configList = ConfigData.ImageConfigList
        else:
            configList = ConfigData.FlavorConfigList
        for config in configList:
            config.showConfig()

# reads the input file and executes the commands
def execCommands():
    configData = ConfigData()
    inputFile = sys.argv[1]
    with open(inputFile,'r') as f:
        for line in f:
            params = [x for x in line.split()]
            if len(params)<3:
                continue
            if params[1].lower() == "config":
                if params[2].lower() == "--hardware":
                    configData.loadConfigData(params[3],CONFIG_TYPES[0])
                elif params[2].lower() == "--images":
                    configData.loadConfigData(params[3],CONFIG_TYPES[1])
                elif params[2].lower() == "--flavors":
                    configData.loadConfigData(params[3],CONFIG_TYPES[2])
                
            elif params[1].lower() == "show":
                if params[2].lower() == "hardware":
                    configData.showConfigData(CONFIG_TYPES[0])
                elif params[2].lower() == "images":
                    configData.showConfigData(CONFIG_TYPES[1])
                elif params[2].lower() == "flavors":
                    configData.showConfigData(CONFIG_TYPES[2])

                
            
if __name__ == "__main__":
    execCommands()
    
