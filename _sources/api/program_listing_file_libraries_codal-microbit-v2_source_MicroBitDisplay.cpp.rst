
.. _program_listing_file_libraries_codal-microbit-v2_source_MicroBitDisplay.cpp:

Program Listing for File MicroBitDisplay.cpp
============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_MicroBitDisplay.cpp>` (``libraries/codal-microbit-v2/source/MicroBitDisplay.cpp``)

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
   
   #include "MicroBitDisplay.h"
   #include "NRFLowLevelTimer.h"
   
   using namespace codal;
   
   MicroBitDisplay::MicroBitDisplay(const MatrixMap &map, uint16_t id) : NRF52LEDMatrix(*new NRFLowLevelTimer(NRF_TIMER4, TIMER4_IRQn), map, id, DisplayMode::DISPLAY_MODE_GREYSCALE), AnimatedDisplay(*this, id)
   {
   }
   
   MicroBitDisplay::~MicroBitDisplay()
   {
   }
