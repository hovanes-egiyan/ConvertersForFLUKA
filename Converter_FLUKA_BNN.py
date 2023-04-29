'''
Created on Mar 24, 2022

@author: Hovanes Egiyan
'''

import sys, string, numpy

class Converter_FLUKA_BNN(object):
    '''
    CLASS to convert the text file output from FLUKA BNN binary file obtained with $FLUPRO/flutil/usbrea 
    to a regular table in a text format. 
    '''


    def __init__(self ):
        '''
        Constructor
        '''
        self.inFileHandle = None 
        self.outFileHandle = None
        
        self.numberOfHeaderLines = 8;
        
        
        self.nX = 280
        self.nY = 140 
        self.nZ = 215 
        
        self.xMin = -70.0
        self.xMax = +70.0
        self.yMin = -70.0
        self.yMax = +70.0
        self.zMin = -60.0
        self.zMax = +370.0
        
        self.data = numpy.zeros( (self.nX,self.nY,self.nZ) )
        
        return


    def readFile(self, inFileName):
        print "Opening file {0} for reading".format( inFileName)            
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
        #Open output file
        if( outFileName == None ) :
            outFileName2Use = inFileName + ".table"
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
                    self.outFileHandle.write( "{0}\t{1}\t{2}\t\t{3} \n".format( x, y, z, self.data[ix,iy,iz] ) )
        
        self.outFileHandle.close()
            
