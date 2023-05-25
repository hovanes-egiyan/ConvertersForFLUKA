#!/usr/bin/python2.7
'''
Created on Mar 24, 2022

@author: Hovanes Egiyan
'''


import sys, string, getopt, os

from optparse import OptionParser

from Converter_FLUKA_BNN import Converter_FLUKA_BNN
from CylindricalConverterKLCPS import CylindricalConverterKLCPS
from RectangularConverterKLCPS import RectangularConverterKLCPS


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
                           action="store", dest="f1", type="string", metavar="InFile", 
                           default="InFile.xml", help="Define input file name to be updated" )
        parser.add_option( "-2", "--f2", 
                           action="store", dest="f2", type="string", metavar="OutFile", 
                           default=None, help="Define new output file" )
        parser.add_option( "-d", "--datatype", 
                           action="store", dest="dataType", type="string", metavar="DataType", 
                           default="PavelCyl", help="Data type in the input file" )
        
        (opts, args) = parser.parse_args( argList )
        
        # Assign the elements of the dictionary to the parsed option values
        self.optionDict["InFile"]  = opts.f1
        self.optionDict["OutFile"] = opts.f2
        self.optionDict["DataType"] = opts.dataType
        
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

    inFileName = progOpts.getOption( "InFile" )
    outFileName = progOpts.getOption( "OutFile" )
    
    print "Input file is {0} , output file is {1}".format(inFileName, outFileName )  
    
    if( progOpts.getOption("DataType") == "PavelCyl" ):
        print "Pavel's cylindrical coordinate system is expected now."
        converter = CylindricalConverterKLCPS()
    elif( progOpts.getOption("DataType") == "PavelRec" ):
        print "Pavel's rectangular coordinate system is expected now."        
        converter = RectangularConverterKLCPS()
    else:
        converter = Converter_FLUKA_BNN()
        
    converter.readFile( inFileName )
    converter.writeFile(outFileName)
    
