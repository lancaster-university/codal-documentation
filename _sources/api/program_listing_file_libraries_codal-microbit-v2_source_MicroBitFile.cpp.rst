
.. _program_listing_file_libraries_codal-microbit-v2_source_MicroBitFile.cpp:

Program Listing for File MicroBitFile.cpp
=========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_MicroBitFile.cpp>` (``libraries/codal-microbit-v2/source/MicroBitFile.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   Copyright (c) 2016 British Broadcasting Corporation.
   This software is provided by Lancaster University by arrangement with the BBC.
   Permission is hereby granted, free of charge, to any person obtaining a
   copy of this software and associated documentation files (the "Software"),
   to deal in the Software without restriction, including without limitation
   the rights to use, copy, modify, merge, publish, distribute, sublicense,
   and/or sell copies of the Software, and to permit persons to whom the
   Software is furnished to do so, subject to the following conditions:
   The above copyright notice and this permission notice shall be included in
   all copies or substantial portions of the Software.
   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
   DEALINGS IN THE SOFTWARE.
   */
   
   #include "MicroBitFile.h"
   #include "ErrorNo.h"
   
   MicroBitFile::MicroBitFile(ManagedString fileName, int mode)
   {
       this->fileName = fileName;
   
       MicroBitFileSystem* fs;
   
       if(MicroBitFileSystem::defaultFileSystem == NULL)
           fs = new MicroBitFileSystem();
       else
           fs = MicroBitFileSystem::defaultFileSystem;
   
       fileHandle = fs->open(fileName.toCharArray(), mode);
   }
   
   int MicroBitFile::setPosition(int offset)
   {
       if(fileHandle < 0)
           return MICROBIT_NOT_SUPPORTED;
   
       if(offset < 0)
           return MICROBIT_INVALID_PARAMETER;
   
       return MicroBitFileSystem::defaultFileSystem->seek(fileHandle, offset, MB_SEEK_SET);
   }
   
   int MicroBitFile::getPosition()
   {
       if(fileHandle < 0)
           return MICROBIT_NOT_SUPPORTED;
   
       return MicroBitFileSystem::defaultFileSystem->seek(fileHandle, 0, MB_SEEK_CUR);
   }
   
   int MicroBitFile::write(const char *bytes, int len)
   {
       if(fileHandle < 0)
           return MICROBIT_NOT_SUPPORTED;
   
       return MicroBitFileSystem::defaultFileSystem->write(fileHandle, (uint8_t*)bytes, len);
   }
   
   int MicroBitFile::write(ManagedString s)
   {
       return write(s.toCharArray(), s.length());
   }
   
   int MicroBitFile::read()
   {
       if(fileHandle < 0)
           return MICROBIT_NOT_SUPPORTED;
   
       char c;
   
       int ret = read( &c, 1);
       
       if ( ret > 0)
         return c;
       
       return ret < 0 ? ret : MICROBIT_NO_DATA;
   }
   
   int MicroBitFile::read(char *buffer, int size)
   {
       if(fileHandle < 0)
           return MICROBIT_NOT_SUPPORTED;
   
       if(size < 0 || buffer == NULL)
           return MICROBIT_INVALID_PARAMETER;
   
       return MicroBitFileSystem::defaultFileSystem->read(fileHandle, (uint8_t*)buffer, size);
   }
   
   ManagedString MicroBitFile::read(int size)
   {
       char buff[size + 1];
   
       buff[size] = 0;
   
       int ret = read(buff, size);
   
       if(ret < 0)
           return ManagedString();
   
       return ManagedString(buff,ret);
   }
   
   int MicroBitFile::remove()
   {
       if ( fileHandle >= 0)
           close();
   
       int ret = MicroBitFileSystem::defaultFileSystem->remove(fileName.toCharArray());
   
       if(ret < 0)
           return ret;
   
       fileHandle = MICROBIT_NOT_SUPPORTED;
   
       return ret;
   }
   
   int MicroBitFile::append(const char *bytes, int len)
   {
       if(fileHandle < 0)
           return MICROBIT_NOT_SUPPORTED;
   
       int ret =  MicroBitFileSystem::defaultFileSystem->seek(fileHandle, 0, MB_SEEK_END);
   
       if(ret < 0)
           return ret;
   
       return write(bytes,len);
   }
   
   int MicroBitFile::append(ManagedString s)
   {
       return append(s.toCharArray(), s.length());
   }
   
   bool MicroBitFile::isValid()
   {
       return fileHandle >= 0;
   }
   
   int MicroBitFile::getHandle()
   {
       return fileHandle;
   }
   
   int MicroBitFile::close()
   {
       if(fileHandle < 0)
           return MICROBIT_NOT_SUPPORTED;
   
       int ret = MicroBitFileSystem::defaultFileSystem->close(fileHandle);
   
       if(ret < 0)
           return ret;
   
       fileHandle = MICROBIT_NO_RESOURCES;
   
       return ret;
   }
   
   int MicroBitFile::flush()
   {
       if(fileHandle < 0)
           return MICROBIT_NOT_SUPPORTED;
   
       return MicroBitFileSystem::defaultFileSystem->flush(fileHandle);
   }
   
   MicroBitFile::~MicroBitFile()
   {
       close();
   }
