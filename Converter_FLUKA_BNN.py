'''
Created on Mar 24, 2022

@author: Hovanes Egiyan
'''

import sys, string, numpy, math

class Converter_FLUKA_BNN(object):
    '''
    CLASS to convert the text file output from FLUKA BNN binary file obtained with $FLUPRO/flutil/usbrea 
    to a regular table in a text format. 
    '''


    def __init__(self ):
        '''
        Constructor
        '''
        
        self.inputFileName = None
        self.outputFileName = None 
        
        self.inFileHandle = None 
        self.outFileHandle = None
        
        self.numberOfHeaderLines = 8;

        self.gev2kw = 5.0       # Conversion constant from GeV/cm^3/sec for 5uA and 12Gev to KW/cm^3.
        
#         Vitaly's coarse binning
#         self.nX = 280
#         self.nY = 140 
#         self.nZ = 215 
#         
#         self.xMin = -70.
#         self.xMax = +70.
#         self.yMin = -70.
#         self.yMax = +70.
#         self.zMin = -60.
#         self.zMax = +370.
        
# Viltay's fine binning         
#         self.nX = 88
#         self.nY = 540 
#         self.nZ = 265
#         
#         self.xMin = -2.2
#         self.xMax = +2.2
#         self.yMin = -13.5
#         self.yMax = +13.5
#         self.zMin = +78.
#         self.zMax = +131.

# Vitaly's new rectangular binning 
#        self.nX = 400           #nx
#        self.nY = 400           #nY
#        self.nZ = 120           #nZ
        
#        self.xMin = -5          # xMin
#        self.xMax = +5          # xMax
#        self.yMin = -5          # yMin
#        self.yMax = +5          # yMax
#        self.zMin = 90          # zMin
#        self.zMax = 150         # zMax

# Vitaly's new cylidircal binning 
        self.nX = 440           #nx
        self.nY = 80            #nY
        self.nZ = 680           #nZ
        
        self.xMin = 2.9250E-01          # rMin
        self.xMax = 1.1292E+01          # rMax
        self.yMin = -3.1416E+00         # phiMin
        self.yMax = 3.1416E+00          # phiMax
        self.zMin = 35          # zMin
        self.zMax = 375         # zMax


# Viltay's coarse binning         
#        self.nX = 88
#        self.nY = 96 
#        self.nZ = 460
         
#        self.xMin = -22.
#        self.xMax = +22.
#        self.yMin = -24.
#        self.yMax = +24.
#        self.zMin = +35.
#        self.zMax = +265.

 
# Pavel's fine binning for cylindrical grid         
#        self.nX = 320
#        self.nY = 144 
#        self.nZ = 188
        
#        self.xMin = 0.0      # rMin
#        self.xMax = 8.0      # rMAx
#        self.yMin = -3.1416  # phiMin
#        self.yMax = +3.1416  # phiMax
#        self.zMin = 0.       # zMin
#        self.zMax = 94.0     # zMax

# Pavel's fine binning for rectangular grid       
#        self.nX = 401
#        self.nY = 401 
#        self.nZ = 188
#        
#        self.xMin = -10.16  # xMin
#        self.xMax = +10.16  # xMAx
#        self.yMin = -12.16  # yMin
#        self.yMax =  +8.16  # yMax
#        self.zMin = 0.      # zMin
#        self.zMax = 94.0    # zMax


        self.data = numpy.zeros( (self.nX,self.nY,self.nZ) )
        
        return


    def readFile(self, inFileName):
        print "Opening file {0} for reading".format( inFileName)       
        self.inputFileName =  inFileName    
        # Open input file
        try :
            self.inFileHandle = open( inFileName, "r" )
        except IOError as err:
            raise err
        
        lineNumber = 0
        iData = 0

        for inputLine in self.inFileHandle:
            lineNumber += 1
#            print lineNumber, " ", inputLine
            if( lineNumber <= self.numberOfHeaderLines ) : 
#                print " HEADER : " , inputLine
                continue
            vecElements = inputLine.split()
            for data in vecElements:
                iz = iData / ( self.nX * self.nY )
                iy = ( iData % ( self.nX * self.nY ) ) / self.nX 
                ix = ( iData % ( self.nX * self.nY ) ) % self.nX 
                
#                print "Point #{0} , ix={1}, iy={2}, iz={3}, value={4}".format(iData, ix, iy, iz, data )   
                if( ix < self.nX and iy < self.nY and iz < self.nZ ) :            
                    self.data[ix,iy,iz] = data 
                iData += 1
#                sys.stdout.write(data)
#            print
            
        return 
     
    def writeFile(self, outFileName = None ):    
        self.outputFileName = outFileName     
        #Open output file
        if( self.outputFileName == None ) :
            outFileName2Use = self.inputFileName + ".table"
        else :
            outFileName2Use = outFileName 
            
        print "Opening file {0} for writing".format( outFileName2Use)    
        try :
            self.outFileHandle = open( outFileName2Use, "w" )
        except IOError as err:
            raise err
        
        for ix in range ( 0, self.nX ) :
            for iy in range( 0, self.nY ) :
                for iz in range( 0, self.nZ ) :
                    x = self.xMin + (ix+0.5) * ( self.xMax - self.xMin ) / self.nX
                    y = self.yMin + (iy+0.5) * ( self.yMax - self.yMin ) / self.nY
                    z = self.zMin + (iz+0.5) * ( self.zMax - self.zMin ) / self.nZ
                    self.outFileHandle.write( "{0} , \t{1} , \t{2} , \t{3}\n".format( x, y, z, self.gev2kw*self.data[ix,iy,iz] ) )
        
        self.outFileHandle.close()

        return
            
