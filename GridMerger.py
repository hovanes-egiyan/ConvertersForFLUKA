'''
Created on Aug 30, 2023


@author: Hovanes Egiyan
'''

#import sys, math, numpy

import math
from scipy.interpolate import LinearNDInterpolator
import numpy as np

from Converter_FLUKA_BNN import Converter_FLUKA_BNN 


class GridMerger(object):
    '''
    This class  takes two converters for FLUKA bnn output and combines them into a single table. 
    The binning grid of the first files should be a multiple of the second one,t that is the second file should have 
    finer binning with the same edges, but the number of bins in all three dimensions of the second file should be 
    multiples of of the number of bins in the first file. 
    '''

    diffToler = 1.0e-8      # Zero tolerance for coordinate differences
    gev2kw = 5.0            # Conversion constant from GeV/cm^3/sec for 5uA and 12Gev to KW/cm^3.


    def __init__(self, coarseGrid, fineGrid ):
        '''
        Constructor
        '''
        self.coarseGrid = coarseGrid
        self.fineGrid   = fineGrid
        
        self.coarseWidthX = ( self.coarseGrid.xMax - self.coarseGrid.xMin ) / self.coarseGrid.nX 
        self.coarseWidthY = ( self.coarseGrid.yMax - self.coarseGrid.yMin ) / self.coarseGrid.nY
        self.coarseWidthZ = ( self.coarseGrid.zMax - self.coarseGrid.zMin ) / self.coarseGrid.nZ
        
        self.fineWidthX = ( self.fineGrid.xMax - self.fineGrid.xMin ) / self.fineGrid.nX 
        self.fineWidthY = ( self.fineGrid.yMax - self.fineGrid.yMin ) / self.fineGrid.nY 
        self.fineWidthZ = ( self.fineGrid.zMax - self.fineGrid.zMin ) / self.fineGrid.nZ
   
        print "Z sizes for coarse are ", self.coarseGrid.zMax, self.coarseGrid.zMin, self.coarseGrid.nZ, self.coarseWidthZ
        print "Z sizes for fine are   ", self.fineGrid.zMax, self.fineGrid.zMin, self.fineGrid.nZ, self.fineWidthZ
  
        print "The grid sizes are ", self.isMultiple(self.coarseWidthX, self.fineWidthX) , self.isMultiple(self.coarseWidthY, self.fineWidthY) , self.isMultiple(self.coarseWidthZ, self.fineWidthZ) , GridMerger.diffToler 
   
        # Make sure the grids widths are multiples of each other, otherwise raise Exit exception        
        if  (not self.isMultiple(self.coarseWidthX, self.fineWidthX)) or (not self.isMultiple(self.coarseWidthY, self.fineWidthY)) or (not self.isMultiple(self.coarseWidthZ, self.fineWidthZ)):
            print "The grid for the second converter is not a multiple of the first converter. Exiting ... "
            raise SystemExit
        
        
        # Make sure that the edges line up
        if (not self.isMultiple(abs(self.coarseGrid.xMin - self.fineGrid.xMin), self.fineWidthX)) or (not self.isMultiple(abs(self.coarseGrid.yMin - self.fineGrid.yMin), self.fineWidthY)) or (not self.isMultiple(abs(self.coarseGrid.zMin - self.fineGrid.zMin), self.fineWidthZ)):
            print "The grid edges do not line up. Exiting ... "
            raise SystemExit
          
  
#         self.nX = self.fineGrid.nX
#         self.nY = self.fineGrid.nY 
#         self.nZ = self.fineGrid.nZ 
#  
#         self.xMin = self.fineGrid.xMin
#         self.yMin = self.fineGrid.yMin
#         self.zMin = self.fineGrid.zMin
#         
#         self.xMax = self.fineGrid.xMax
#         self.yMax = self.fineGrid.yMax
#         self.zMax = self.fineGrid.zMax
        
        self.coarseData = np.array(self.coarseGrid.data)
#         self.fineData   = np.array(self.fineGrid.data)
        
        self.extrapolatingFunction = None
        
        return
    
    
    def isMultiple(self, x1, x2 ):
        return ( abs( (x1/x2) - int(x1/x2) ) < GridMerger.diffToler )
    
    def interpolateData(self):
        '''
        Setup interpolation function for the coarse grid
        '''

        linearizedCoarseData = self.coarseData.reshape(-1)
        
        xCoarseArray=[]
        yCoarseArray=[]
        zCoarseArray=[]
        for ix in range(self.coarseGrid.nX):
            xCoarse = self.coarseGrid.xMin + (ix+0.5) * self.coarseWidthX     
            for iy in range(self.coarseGrid.nY):
                yCoarse = self.coarseGrid.yMin + (iy+0.5) * self.coarseWidthY
                for iz in range(self.coarseGrid.nZ):
                    zCoarse = self.coarseGrid.zMin + (iz+0.5) * self.coarseWidthZ
                    xCoarseArray.append(xCoarse)
                    yCoarseArray.append(yCoarse)
                    zCoarseArray.append(zCoarse)
                                        
        self.extrapolatingFunction = LinearNDInterpolator((xCoarseArray, yCoarseArray,zCoarseArray), linearizedCoarseData)
        
        return;
        
    def writeFile(self, outFileName = None ):    
        self.outputFileName = outFileName     
        #Open output file
        if( self.outputFileName == None ) :
            outFileName2Use = "mergedData.table"
        else :
            outFileName2Use = outFileName 
            
        print "Opening file {0} for writing".format( outFileName2Use)    
        try :
            self.outFileHandle = open( outFileName2Use, "w" )
        except IOError as err:
            raise err
        
        # Loop over points within a coarse grid with fine grid steps and calculate the data from interpolation function
        for xLow in range( self.coarseGrid.xMin, self.coarseGrid.xMax,  self.fineWidthX ) :
            x = xLow + 0.5 * self.fineWidthX            
            for yLow in range( self.coarseGrid.yMin, self.coarseGrid.yMax,  self.fineWidthY ) :
                y = yLow + 0.5 * self.fineWidthY                            
                for zLow in range( self.coarseGrid.zMin, self.coarseGrid.zMax,  self.fineWidthZ ) :
                    z = zLow + 0.5 * self.fineWidthZ     
                    
                    if( self.fineData.xMin <= x and x<= self.fineData.xMax ): 
                        idxFineX = ( xLow - self.fineGrid.xMin ) / self.fineWidthX 
                        idxFineY = ( yLow - self.fineGrid.yMin ) / self.fineWidthY 
                        idxFineZ = ( zLow - self.fineGrid.zMin ) / self.fineWidthZ 
                        
                        dataValue = self.fineGrid.data[idxFineX, idxFineY, idxFineZ]
                        
                    else :
                        dataValue = self.extrapolatingFunction(x,y,z)
                            
                    self.outFileHandle.write( "{0} , \t{1} , \t{2} , \t{3}\n".format( x, y, z, GridMerger.gev2kw * dataValue ) )
        
        self.outFileHandle.close()

        return
   
        