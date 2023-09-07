'''
Created on May 16, 2023

@author: Hovanes Egiyan
'''

import sys, math, numpy

from Converter_FLUKA_BNN import Converter_FLUKA_BNN 

class CylindricalConverterCPSHC(Converter_FLUKA_BNN):
    '''
    CLASS to convert the text file output from FLUKA BNN binary file obtained with $FLUPRO/flutil/usbrea 
    to a regular table in a text format. In particular, this is used for cylindrical coordinate system that 
    Pavel uses for CPSHC project for Hall C. 
    '''
    def __init__( self ):
        print ( "Using converter for Pavel's cylindrical reference system for Hall C" )
        super(CylindricalConverterCPSHC, self).__init__()
        self.nX = 160           #nR
        self.nY = 144           #nPhi
        self.nZ = 750           #nZ
        
        self.xMin = 0.0         # rMin
        self.xMax = 4.0         # rMax
        self.yMin = -math.pi    # phiMin
        self.yMax = +math.pi    # phiMax
        self.zMin = -30.0       # zMin
        self.zMax = +45.0       # zMax     
        
        self.data = numpy.zeros( (self.nX,self.nY,self.nZ) )

        return
    
    
    
    def writeFile(self, outFileName = None ):    
        print ( "Will write assuming Pavel's cylindrical reference system for Hall C CPS" )
        self.outputFileName = outFileName     
        #Open output file
        if( self.outputFileName == None ) :
            outFileName2Use = self.inputFileName + ".csv"
        else :
            outFileName2Use = outFileName 
            
        print ( "Opening file {0} for writing".format( outFileName2Use) )    
        try :
            self.outFileHandle = open( outFileName2Use, "w" )
        except IOError as err:
            raise err
        
        '''
        The second column (here Y) of the Pavel's file with cylindrical coordinates is the azimuthal Phi angle  
        defined in -Pi to +Pi range. Here I will treat it differently to have it periodic so 
        that the first/last bin does not get lost. 
        I add the end points -Pi to +Pi, but I change the range to be from -Pi/2 to +3Pi/2. 
        '''
            
        iyFirst = self.nY * ( -math.pi/2. - self.yMin ) / (self.yMax - self.yMin)
            
        for ix in range ( 0, self.nX ) :
            x = self.xMin + (ix+0.5) * ( self.xMax - self.xMin ) / self.nX
                
            y = -math.pi/2.
            for iz in range( 0, self.nZ ) :
                z = self.zMin + (iz+0.5) * ( self.zMax - self.zMin ) / self.nZ
                self.outFileHandle.write( "{0} , \t{1} , \t{2} , \t{3}\n".format( x, y, z, self.gev2kw*(self.data[ix,iyFirst,iz] + self.data[ix,iyFirst-1,iz])/2. ) )

            for iy in range( 0, self.nY ) :
                y = self.yMin + (iy+0.5) * ( self.yMax - self.yMin ) / self.nY
                if( y < (-math.pi/2) ) :
                    y = y + 2.*math.pi
                for iz in range( 0, self.nZ ) :
                    z = self.zMin + (iz+0.5) * ( self.zMax - self.zMin ) / self.nZ
                    self.outFileHandle.write( "{0} , \t{1} , \t{2} , \t{3}\n".format( x, y, z, self.gev2kw*self.data[ix,iy,iz] ) )

            y = +3*math.pi/2.
            for iz in range( 0, self.nZ ) :
                z = self.zMin + (iz+0.5) * ( self.zMax - self.zMin ) / self.nZ
                self.outFileHandle.write( "{0} , \t{1} , \t{2} , \t{3}\n".format( x, y, z, self.gev2kw*(self.data[ix,iyFirst,iz] + self.data[ix,iyFirst-1,iz])/2. ) )
                
        self.outFileHandle.close()
            
        return
        
