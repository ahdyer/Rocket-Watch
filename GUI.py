# Serial Imports
import serial
from serial.serialutil import SerialException
import serial.tools.list_ports as ListPorts

# Plotting tool imports
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D

##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  
##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  

# Arrays to stroe avalilbe and not used COM pports
unusedComPorts = []
allComPorts = []
# Bools for Com port and setting CSV headers on first loop
comPortBusy = False
firstLoop = True

# Array to store all data recieved on serial, in CSV formatt
dataCSV = []
flightState = [] # Stores as number 0: Standby, 1: , 2:
temp = []
pressure = []
sampleCount = []


#Classes

class RTPLOT:
    def __init__(self, axs, ds = 1):
        self.axt = axs[0]
        self.axp = axs[1]
        self.ds = ds
        self.sdata = [0]
        self.tdata = [0]
        self.pdata = [0]
        self.linet = Line2D(self.sdata, self.tdata)
        self.linep = Line2D(self.sdata, self.pdata)
        self.axt.add_line(self.linet)
        self.axp.add_line(self.linep)
        self.axt.set_ylim(0, 30)
        self.axp.set_ylim(0, 30)
        self.axt.set_xlim(0, 2)
        self.axp.set_xlim(0, 2)
    def update(self, data):
        t, p = data
        nextSample = self.sdata[len(self.sdata)-1]+1
        self.axt.set_xlim(0, nextSample)
        self.axp.set_xlim(0, nextSample)
        if len(self.tdata) >= 2:
            lowerLimt = sorted(self.tdata)[1] - 0.1
        else:
            lowerLimt = 0
        if len(self.pdata) >= 2:
            lowerLimp = sorted(self.pdata)[1] - 100
        else:
            lowerLimp = 0
        self.axt.set_ylim(lowerLimt, max(self.tdata)+0.1)
        self.axp.set_ylim(lowerLimp, max(self.pdata)+100)

        self.sdata.append(nextSample)
        self.tdata.append(t)
        self.pdata.append(p)
        self.linet.set_data(self.sdata, self.tdata)
        self.linep.set_data(self.sdata, self.pdata)
        return [self.linet, self.linep]

def UART_READ(comPortBusy, firstLoop):
    while not comPortBusy:
        try:
            lineBytes = AltimeterSerial.readline()
        except Exception as error:
            print(error)
            print("Failed to read line from {}".format(comPort))
            comPortBusy = True
            yield  0, 0
        try:
            lineString = lineBytes.decode('utf-8')
            words = lineString.split()
        except Exception as error:
            print(error)
            print("Failed to decode data and split")
        
        if(len(words) > 5):
            if(firstLoop):
                prevTemp = 0
                prevPres = 0
                lineCSV = words[0] + words[1] + ',' + words[3] + ',' + words[5] + ',' + "Sample:" + '\n'
                currentSample = 0

                firstLoop = False
            else:
                lineCSV = words[2] + ',' + words[4] + ',' + words[6] + ',' + str(currentSample) + '\n'
                currentSample += 1
            if(words[2] == "Standby"):
                flightState.append(0)
            elif(words[2] == "Armed"):
                flightState.append(1)
            #Need to figure out why its coming through as seperate coloumns and the coloumn headings are not working
            dataCSV.append(lineCSV)
            f.write(lineCSV)
            sampleCount.append(currentSample)
            try:
                t = float(words[4])
                prevTemp = t
            except:
                t = prevTemp
            temp.append(t)
            try:
                p = float(words[6])
                prevPres = p
            except:
                p = prevPres
            pressure.append(p)
            yield  t, p
        else:
            yield 0, 0

# plt.rc('lines', linewidth=2.5)
fig, axs  = plt.subplots(2, 1)
axs[0].set_title("Temprature")
axs[1].set_title("Pressure")
fig.set_layout_engine("constrained")
rtplot = RTPLOT(axs)








##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  
##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ##  ## 

# Find Mostly likely COM port to be Altimeter, Print the rest to console for debugging
for port in ListPorts.comports():
    allComPorts.append(port.description)
    if(port.description.find("USB Serial Port") != -1):
        comPort = port.description[port.description.find("(")+1:port.description.find(")")]
        print("Using {}".format(port.description))
    else:
        unusedComPorts.append(port.description)
print("Found the following COM ports that are not being used:")
for port in unusedComPorts:
    print(port)
    


# See if serial port is avalible, if not print error to terminal and set Bool to be used latter
# to ensure we dont try and read from non initalised serial 
try:
    AltimeterSerial = serial.Serial(comPort, 115200)
except Exception as error:
    print(error)
    print("Failed to inatilse COM port {}".format(comPort))
    comPortBusy = True



f = open('csvTest.txt', 'w')



     
ani = animation.FuncAnimation(fig, rtplot.update, UART_READ(comPortBusy, firstLoop), interval=100,  blit=False, save_count = 10)

plt.show()
        


# lineFS = ax.plot(sampleCount, flightState)
print(sampleCount, temp)
# # lineT = ax.plot(sampleCount, temp)
# # lineP = ax.plot(sampleCount, pressure)

# plt.show()

f.close()
    
    

