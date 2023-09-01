#!/usr/bin/python2.7
'''
Created on Mar 24, 2022

This script  takes two text files from FLUKA bnn output and combines them into a single table. 
The binning grid of the first files should be a multiple of the second one,t that is the second file should have 
finer binning with the same edges, but the number of bins in all three dimensions of the second file should be 
multiples of of the number of bins in the first file. 

@author: Hovanes Egiyan
'''


import sys, string, getopt, os

from optparse import OptionParser

from Converter_FLUKA_BNN import Converter_FLUKA_BNN
from CylindricalConverterKLCPS import CylindricalConverterKLCPS
from RectangularConverterKLCPS import RectangularConverterKLCPS
from CylindricalConverterCPSHC import CylindricalConverterCPSHC
from CylindricalConverterVitalyCPS import CylindricalConverterVitalyCPS
from GridMerger import GridMerger


#===============================================================================
# Class to handle command line options
#===============================================================================
class clfOptions:
    """ Class to handle command line options  """
        
    # Constructor
    def __init__( self, argList ):
        self.optionDict = {}
        # Command line
        try:
            # Get options from command line, may get overriden 
            self.parseCommandLine( argList )  
        except getopt.GetoptError as errMsg:
            print errMsg
            self.printHelpMessage()
            sys.exit(-1)
        return
    
    
    # Parse command file and append the option list extracted from the command file
    def parseCommandLine( self, argList ):
        print "Starting command line parsing:", argList
        # Here I am using optparse module which may be obsolete in future Python versions 
        # This part might need to be redone for it to work with Python 3.1
        # Python does not seem to be forward or backward compatible
        parser = OptionParser(usage = "usage: %prog [options] ")
        parser.add_option( "-1", "--f1", 
                           action="store", dest="f1", type="string", metavar="InFileCoarse", 
                           default="InFileCoarse.lis", help="Define input file name with coarse binning" )
        parser.add_option( "-2", "--f2", 
                           action="store", dest="f2", type="string", metavar="InFileFine", 
                           default="InFileFine.lis", help="Define input file name with fine binning" )        
        parser.add_option( "-3", "--f3", 
                           action="store", dest="f3", type="string", metavar="OutFile", 
                           default=None, help="Define new output file" )
        parser.add_option( "-d", "--datatype", 
                           action="store", dest="dataType", type="string", metavar="DataType", 
                           default="None", help="Data type in the input files" )
        
        (opts, args) = parser.parse_args( argList )
        
        # Assign the elements of the dictionary to the parsed option values
        self.optionDict["InFileCoarse"]  = opts.f1
        self.optionDict["InFileFine"]    = opts.f2
        self.optionDict["OutFile"]       = opts.f3
        self.optionDict["DataType"]      = opts.dataType
        
        return
        
        
        
    # Return option for key optKey if exists, otherwise return None
    def getOption(self, optKey):
        if optKey in self.optionDict:
            return self.optionDict[optKey]
        else :
            return None


    # Returns the dictionary of all options
    def getOptions(self):
        return self.optionDict

        
if __name__ == '__main__':
    
    globOptions = clfOptions( sys.argv[1:] )

    # Get the global options from the clfOptions class
    progOpts = globOptions

    inFileCoarseName = progOpts.getOption( "InFileCoarse" )
    inFileFineName   = progOpts.getOption( "InFileFine" )
    outFileName      = progOpts.getOption( "OutFile" )
    
    print "Input file with coarse binning is {0} , Input file with fine binning is {1} , output file is {2}".format(inFileCoarseName, inFileFineName, outFileName )  
    
    if( progOpts.getOption("DataType") == "PavelCyl" ):
        print "Pavel's KLCPS cylindrical coordinate system is expected now."
        converterCoarse = CylindricalConverterKLCPS()
        converterFine = CylindricalConverterKLCPS()
    elif( progOpts.getOption("DataType") == "PavelRec" ):
        print "Pavel's KLCPS rectangular coordinate system is expected now."        
        converterCoarse = RectangularConverterKLCPS()
        converterFine = RectangularConverterKLCPS()
    elif( progOpts.getOption("DataType") == "PavelHC" ):
        print "Pavel's HC CPS cylindrical coordinate system is expected now."        
        converterCoarse = CylindricalConverterCPSHC()
        converterFine = RectangularConverterKLCPS()
    elif( progOpts.getOption("DataType") == "VitalyCyl" ):
        print "Vitaly's CPS cylindrical coordinate system is expected now."
        converterCoarse = CylindricalConverterVitalyCPS()
        converterFine = CylindricalConverterVitalyCPS()
              
    else:
        converterCoarse = Converter_FLUKA_BNN()
        converterFine = Converter_FLUKA_BNN()
        
        
    converterCoarse.readFile( inFileCoarseName )
    converterFine.readFile( inFileFineName )
    
    converterMerger = GridMerger( converterCoarse, converterFine )
    
#    converterMerger.writeCoarseFile(outFileName)

    converterMerger.interpolateData()
    converterMerger.writeFineFile(outFileName)
    
