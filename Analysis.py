import numpy as np
import matplotlib.pyplot as plt


"""

Analysis Functionality 

- Calculate max values
- Calculate mean, rms, std1/2
- Generate plots
"""

class Analysis:

    def __init__(self, images, trials=1):
        self.trials = trials
        self.images = images
        self.maxUV = np.empty(trials)
        self.maxBlue = np.empty(trials)

    #Statistical Helper Functions

    def findMax(self):
        
        self.maxUV = np.max(self.images[0])
        self.maxBlue = np.max(self.images[1])
        
        print("Max UV = {}, Max B = {}".format(self.maxUV, self.maxBlue))
        
        return self.maxUV, self.maxBlue

    def calcMean(self):
        
        self.mean = np.mean(self.maxUV - self.maxBlue)
        
        print("Mean = ", self.mean)
        
        return self.mean

    def calcRMSError(self):
        
        self.RMSError = np.sqrt(np.mean((self.maxUV-self.maxBlue)**2))
        
        print("RMS Error = ", self.RMSError)
        return self.RMSError

    def calcStdDev(self):
        self.stdUV = np.std(self.maxUV)
        self.stdBlue = np.std(self.maxBlue)
        
        print("Std Dev UV = {}, Std Dev Blue = {}".format(self.stdUV, self.stdBlue))

        return self.stdUV, self.stdBlue

    def calcStats(self):
        return self.calcMean(), self.calcRMSError(), self.calcStdDev()
    
    #Plot the maximum values for UV and Blue LED

    def imagePlots(self, blk=False):
        plt.figure()
        plt.subplot(121)
        plt.imshow(self.images[0],cmap="hot",vmin=0,vmax=4095)
        plt.title('Blue')
        plt.subplot(122)
        plt.imshow(self.images[1],cmap="hot",vmin=0,vmax=4095)
        plt.title('UV')
        plt.ion()
        plt.pause(.001)
        plt.show(block=blk)

    def generatePlots(self):
        

        plt.figure()
        plt.plot(self.maxUV,'r',label='UV')
        plt.plot(self.maxBlue,'b',label='Blue')
        plt.legend()
        plt.ylim([0,4096])
        plt.show() 
        
#        plt.figure()       
#        plt.plot(self.maxUV,'r',label='UV')
#        plt.plot(self.maxBlue,'b',label='Blue')
#        plt.legend()
#        plt.ylim([0,4096])
#        plt.show()
#    

