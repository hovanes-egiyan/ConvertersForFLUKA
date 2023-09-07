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

        self.gev2kw = 5.0        # Conversion constant from GeV/cm^3/sec for 5uA and 12Gev to KW/cm^3.
        
        self.nX = None           # nx
        self.nY = None           # nY
        self.nZ = None           # nZ
        
        self.xMin = None         # rMin
        self.xMax = None         # rMax
        self.yMin = None         # phiMin
        self.yMax = None         # phiMax
        self.zMin = None         # zMin
        self.zMax = None         # zMax

        self.data = None
        
        return


    def readFile(self, inFileName):
        print ( "Opening file {0} for reading".format( inFileName) )       
        self.inputFileName =  inFileName    
        # Open input file
        try :
            self.inFileHandle = open( inFileName, "r" )
        except IOError as err:
            raise err
        
        lineNumber = 0
        iData = 0

        lowLim = []
        hiLim  = []
        nBins  = []

        for inputLine in self.inFileHandle:
            lineNumber += 1
#            print lineNumber, " ", inputLine
            if( lineNumber <= self.numberOfHeaderLines ) : 
#                print " HEADER : " , inputLine
                headerElements = inputLine.split()
                print ( headerElements )
                if( len(headerElements) >= 9 and headerElements[1] == "coordinate:" and  headerElements[2] == "from" ):
                    lowLim.append( float( headerElements[3] ) )
                    hiLim.append ( float( headerElements[5] ) )
                    nBins.append ( int  ( headerElements[7] ) )
                if( lineNumber == self.numberOfHeaderLines ) : 
                    if( len(nBins)  == 3 ):
                        self.nX = nBins[0]           #nx
                        self.nY = nBins[1]           #nY
                        self.nZ = nBins[2]           #nZ

                        self.xMin = lowLim[0]        # rMin
                        self.xMax = hiLim[0]         # rMax
                        self.yMin = lowLim[1]        # phiMin
                        self.yMax = hiLim[1]         # phiMax
                        self.zMin = lowLim[2]        # zMin
                        self.zMax = hiLim[2]         # zMax

                        self.data = numpy.zeros( (self.nX,self.nY,self.nZ) )

                    else :
                        print ( "The data dimension in the header is not equal to 3. Exiting ..." )
                        raise RuntimeError

                    print ( self.nX, self.nY, self.nZ ) 
                continue 

            vecElements = inputLine.split()
            for data in vecElements:
                iz = int( iData / ( self.nX * self.nY ) )
                iy = int( ( iData % ( self.nX * self.nY ) ) / self.nX )
                ix = int( ( iData % ( self.nX * self.nY ) ) % self.nX )
                
#                print ( "Point #{0} , ix={1}, iy={2}, iz={3}, value={4}".format(iData, ix, iy, iz, data ) )   
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
            
        print ( "Opening file {0} for writing".format( outFileName2Use) )    
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
            
