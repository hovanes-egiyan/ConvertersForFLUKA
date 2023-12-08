'''
Created on Aug 30, 2023


@author: Hovanes Egiyan
'''

#import sys, math, numpy

import math
from scipy.interpolate import LinearNDInterpolator
from scipy.interpolate import RegularGridInterpolator

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
   
        print ( "X sizes for coarse are ", self.coarseGrid.xMax, self.coarseGrid.xMin, self.coarseGrid.nX, self.coarseWidthX )
        print ( "X sizes for fine are   ", self.fineGrid.xMax, self.fineGrid.xMin, self.fineGrid.nX, self.fineWidthX )
  
        print ( "The grid sizes are ", self.isMultiple(self.coarseWidthX, self.fineWidthX) , self.isMultiple(self.coarseWidthY, self.fineWidthY) , self.isMultiple(self.coarseWidthZ, self.fineWidthZ) , GridMerger.diffToler )
   
        # Make sure the grids widths are multiples of each other, otherwise raise Exit exception        
        if  (not self.isMultiple(self.coarseWidthX, self.fineWidthX)) or (not self.isMultiple(self.coarseWidthY, self.fineWidthY)) or (not self.isMultiple(self.coarseWidthZ, self.fineWidthZ)):
            print ("The grid for the second converter is not a multiple of the first converter. Exiting ... " )
            raise SystemExit
        
        
        # Make sure that the edges line up
        if (not self.isMultiple(abs(self.coarseGrid.xMin - self.fineGrid.xMin), self.fineWidthX)) or (not self.isMultiple(abs(self.coarseGrid.yMin - self.fineGrid.yMin), self.fineWidthY)) or (not self.isMultiple(abs(self.coarseGrid.zMin - self.fineGrid.zMin), self.fineWidthZ)):
            print ( "The grid edges do not line up. Exiting ... " )
            raise SystemExit
          
  
        self.coarseData = np.array(self.coarseGrid.data)
#        self.fineData   = np.array(self.fineGrid.data)
        
        self.interpolatingFunction = None
        self.ipCoarseData  = None 
        self.xMesh = None
        self.yMesh = None
        self.zMesh = None
                      
        return
    
    
    def isMultiple(self, x1, x2 ):
        return bool( abs( (x1/x2) - int(x1/x2) ) < GridMerger.diffToler )
    
    def interpolateData(self):
        '''
        Setup interpolation function for the coarse grid
        '''
        print ( "In the function to interpolate data" )

#        linearizedCoarseData = self.coarseData.reshape(-1)
        
        xCoarseArray=[]
        yCoarseArray=[]
        zCoarseArray=[]
        for ix in range(self.coarseGrid.nX):
            xCoarse = self.coarseGrid.xMin + (ix+0.5) * self.coarseWidthX   
            xCoarseArray.append(xCoarse)            
            # print "ix is {0} , xCoarse is {1}".format(ix,xCoarse)  
        for iy in range(self.coarseGrid.nY):
            yCoarse = self.coarseGrid.yMin + (iy+0.5) * self.coarseWidthY
            yCoarseArray.append(yCoarse)                
        for iz in range(self.coarseGrid.nZ):
            zCoarse = self.coarseGrid.zMin + (iz+0.5) * self.coarseWidthZ
            zCoarseArray.append(zCoarse)                  
        print ( xCoarseArray )
        print ( yCoarseArray )
        print ( zCoarseArray )
        print ( "Calling interpolating function" )
#        self.interpolatingFunction = LinearNDInterpolator(list(zip(xCoarseArray, yCoarseArray,zCoarseArray)), linearizedCoarseData)
        interpolatingFunction = RegularGridInterpolator( (xCoarseArray, yCoarseArray,zCoarseArray), self.coarseData, method='linear', bounds_error=False, fill_value=0 )
        
        print ( self.coarseGrid.yMax, self.coarseGrid.yMin, self.fineGrid.nY )
        
        # Create mesh for the interpolation
        xFineArray = np.linspace( self.coarseGrid.xMin + 0.5*self.coarseWidthX, self.coarseGrid.xMax - 0.5*self.coarseWidthX, int( (self.coarseGrid.xMax - self.coarseGrid.xMin ) / self.fineWidthX ) )
        yFineArray = np.linspace( self.coarseGrid.yMin + 0.5*self.coarseWidthY, self.coarseGrid.yMax - 0.5*self.coarseWidthY, int( (self.coarseGrid.yMax - self.coarseGrid.yMin ) / self.fineWidthX ) )
        zFineArray = np.linspace( self.coarseGrid.zMin + 0.5*self.coarseWidthZ, self.coarseGrid.zMax - 0.5*self.coarseWidthZ, int( (self.coarseGrid.zMax - self.coarseGrid.zMin ) / self.fineWidthX ) )
        
        print ( "Array X is " , xFineArray ) 
        print ( "Array Y is " , yFineArray )
        print ( "Array Z is " , zFineArray )
        
        print ( "Creating mesh" )
        self.xMesh, self.yMesh, self.zMesh = np.meshgrid(xFineArray, yFineArray, zFineArray, indexing='ij', sparse=True ) 
      
        print ( "Filling the mesh " )
#        self.ipCoarseData = interpolatingFunction((self.xMesh, self.yMesh, self.zMesh))
              
        # print self.ipCoarseData
        
        print ( "Interpolation is complete" )
        return;
        
    def writeFineFile(self, outFileName = None ):    
        self.outputFileName = outFileName     
        #Open output file
        if( self.outputFileName == None ) :
            outFileName2Use = "mergedData.table"
        else :
            outFileName2Use = outFileName 
            
        print ( "Opening file {0} for writing".format( outFileName2Use ) )    
        try :
            self.outFileHandle = open( outFileName2Use, "w" )
        except IOError as err:
            raise err
         
        # Loop over points within a coarse grid with fine grid steps and calculate the data from interpolation function or the fine grid      
        ix=-1
        for x in self.xMesh :
            ix += 1
            iy=-1            
            for y in self.yMesh :
                iy += 1 
                iz=-1                
                for z in self.zMesh :
                    iz += 1
                    if( self.fineGrid.xMin <= x and x <= self.fineGrid.xMax ) and ( self.fineGrid.yMin <= y and y <= self.fineGrid.yMax ) and ( self.fineGrid.zMin <= z and z <= self.fineGrid.zMax ) : 
                        idxFineX = int( ( x - self.fineGrid.xMin ) / self.fineWidthX ) 
                        idxFineY = int( ( y - self.fineGrid.yMin ) / self.fineWidthY )
                        idxFineZ = int( ( z - self.fineGrid.zMin ) / self.fineWidthZ )                   
                        dataValue = self.fineGrid.data[idxFineX, idxFineY, idxFineZ]
                    else :
#                        dataValue = self.ipCoarseData[ix,iy,iz]
                        dataValue = -9999
                    self.outFileHandle.write( "{0:8.3f} , \t{1:8.3f} , \t{2:8.3f} , \t{3:12.6f}\n".format( x, y, z, GridMerger.gev2kw * dataValue[0] ) )

                    
        
        self.outFileHandle.close()

        return
   
    def writeCoarseFile(self, outFileName = None ):    
        self.outputFileName = outFileName     
        #Open output file
        if( self.outputFileName == None ) :
            outFileName2Use = "mergedData.csv"
        else :
            outFileName2Use = outFileName 
            
        print ( "Opening file {0} for writing".format( outFileName2Use) )    
        try :
            self.outFileHandle = open( outFileName2Use, "w" )
        except IOError as err:
            raise err
        
        xCoarseArray = np.linspace( self.coarseGrid.xMin + 0.5*self.coarseWidthX, self.coarseGrid.xMax - 0.5*self.coarseWidthX, self.coarseGrid.nX  )
        yCoarseArray = np.linspace( self.coarseGrid.yMin + 0.5*self.coarseWidthY, self.coarseGrid.yMax - 0.5*self.coarseWidthY, self.coarseGrid.nY  )
        zCoarseArray = np.linspace( self.coarseGrid.zMin + 0.5*self.coarseWidthZ, self.coarseGrid.zMax - 0.5*self.coarseWidthZ, self.coarseGrid.nZ  )


        print ( xCoarseArray )
        print ( yCoarseArray )
        print ( zCoarseArray )
         
        # Loop over points within a coarse grid with fine grid steps and calculate the data from interpolation function or the fine grid      
        ix=-1
        for x in xCoarseArray :
            ix += 1
            iy=-1
            for y in yCoarseArray :
                iy += 1 
                iz=-1                
                for z in zCoarseArray :
                    iz += 1
                    if not (( self.fineGrid.xMin <= x and x <= self.fineGrid.xMax ) and ( self.fineGrid.yMin <= y and y <= self.fineGrid.yMax ) and ( self.fineGrid.zMin <= z and z <= self.fineGrid.zMax )) : 
                        dataValue = self.coarseGrid.data[ix,iy,iz]
                        self.outFileHandle.write( "{0:8.3f} , \t{1:8.3f} , \t{2:8.3f} , \t{3:12.6e}\n".format( x, y, z, GridMerger.gev2kw * dataValue ) )


        for ix in range(self.fineGrid.nX) :
            for iy in range(self.fineGrid.nY) :
                for iz in range(self.fineGrid.nZ) :
                    dataValue = self.fineGrid.data[ix, iy, iz]
                    
                    x = self.fineGrid.xMin + (ix+0.5) * self.fineWidthX   
                    y = self.fineGrid.yMin + (iy+0.5) * self.fineWidthY   
                    z = self.fineGrid.zMin + (iz+0.5) * self.fineWidthZ   

                    self.outFileHandle.write( "{0:8.3f} , \t{1:8.3f} , \t{2:8.3f} , \t{3:12.6e}\n".format( x, y, z, GridMerger.gev2kw * dataValue ) )
                    
        
        self.outFileHandle.close()

        return

        