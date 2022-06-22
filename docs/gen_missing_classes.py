#!/usr/bin/env python3

# The MIT License (MIT)

# Copyright (c) 2022 Lancaster University.

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from fileinput import filename
from genericpath import exists
from pathlib import Path
import os

ROOT = os.getcwd()
LIBPATH = os.path.join( ROOT, "libraries" )
EXCLUDE = [ 'codal', 'codal-bootstrap', 'codal-nrf52', 'codal-microbit-nrf5sdk' ]

OUTPUT = "docs/source/api"

def makeNewDoc( path ):
    print( "..." )

def isCpp( file ):
    for ext in [ "cpp", "c", "hpp", "h" ]:
        if( str(file).endswith( ext ) ):
            return True
    return False

def buildFileList( path ):
    list = []
    for file in os.listdir( path ):
        filePath = os.path.join( path, file )
        if( os.path.isdir( filePath ) ):
            list.extend( buildFileList( filePath ) )
        else:
            if( isCpp( filePath ) ):
                list.append( os.path.relpath( filePath, LIBPATH ) )
    
    return list;

def includeLib( path ):
    for prefix in EXCLUDE:
        if( str(path).startswith( F"{prefix}{os.path.sep}") ):
            return False
    return True


# Check we have an output path
outputPath = os.path.join( ROOT, OUTPUT )
if( not exists( outputPath ) ):
    os.makedirs( outputPath, exist_ok=True )

list = buildFileList( LIBPATH )
index = []

for file in list:
    if( not includeLib( file ) ):
        continue

    fileName = Path( file ).stem
    docName = F"{fileName}.rst"

    # Do we have an output path for this?
    srcPath  = os.path.join( LIBPATH, file )
    destPath = os.path.join( outputPath, os.path.dirname(file), docName )
    rstPath  = os.path.join( outputPath, os.path.dirname(file), fileName )
    if( not exists( os.path.dirname(destPath) ) ):
        print( F"Added missing path: {os.path.dirname(destPath)}" )
        os.makedirs( os.path.dirname(destPath) )
    
    # Do we need to build a template file?
    if( not exists( destPath ) ):
        print( F"Creating template file: {destPath}" )

        with open( destPath, 'w' ) as genFile:
            genFile.writelines(
                [
                    F"{fileName}\n",
                    "============\n",
                    "\n",
                    F".. doxygenclass:: codal::{fileName}\n",
                ]
            )

    # Update the global index
    index.append( os.path.relpath( rstPath, OUTPUT ) )

for rstRef in index:
    print( rstRef )