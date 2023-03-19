
.. _program_listing_file_libraries_codal-core_source_driver-models_Display.cpp:

Program Listing for File Display.cpp
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_Display.cpp>` (``libraries/codal-core/source/driver-models/Display.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   
   Copyright (c) 2017 Lancaster University.
   
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
   
   #include "Display.h"
   #include "ErrorNo.h"
   
   using namespace codal;
   
   Display::Display(int width, int height, uint16_t id) : image(width, height)
   {
       this->width = width;
       this->height = height;
       this->brightness = 255;
       this->id = id;
   }
   
   int Display::getWidth()
   {
       return width;
   }
   
   int Display::getHeight()
   {
       return height;
   }
   
   int Display::setBrightness(int b)
   {
       //sanitise the brightness level
       if(b < 0 || b > 255)
           return DEVICE_INVALID_PARAMETER;
   
       this->brightness = b;
   
       return DEVICE_OK;
   }
   
   
   int Display::getBrightness()
   {
       return this->brightness;
   }
   
   
   void Display::enable()
   {
   }
   
   void Display::disable()
   {
   }
   
   Image Display::screenShot()
   {
       return image.crop(0,0, width, height);
   }
   
   
   Display::~Display()
   {
   }
