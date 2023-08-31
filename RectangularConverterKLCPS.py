'''
Created on May 16, 2023

@author: Hovanes Egiyan
'''

import sys, math, numpy

from Converter_FLUKA_BNN import Converter_FLUKA_BNN 

class RectangularConverterKLCPS(Converter_FLUKA_BNN):
    '''
    CLASS to convert the text file output from FLUKA BNN binary file obtained with $FLUPRO/flutil/usbrea 
    to a regular table in a text format. In particular, this is used for rectangular coordinate system that 
    Pavel uses for KLCPS project. 
    '''
    def __init__( self ):
        print "Using converter for Pavel's rectangular reference system for Hall D"
        super(RectangularConverterKLCPS, self).__init__()
        self.nX = 401           #nR
        self.nY = 400           #nPhi
        self.nZ = 228           #nZ
        
        self.xMin = -1.0250e+01    # rMin
        self.xMax = +1.0250e+01    # rMax
        self.yMin = -1.2000e+01    # phiMin
        self.yMax = +8.0000e+00    # phiMax
        self.zMin = -20.           # zMin
        self.zMax = +94.0          # zMax
                
        self.data = numpy.zeros( (self.nX,self.nY,self.nZ) )

        return
    
    
    
