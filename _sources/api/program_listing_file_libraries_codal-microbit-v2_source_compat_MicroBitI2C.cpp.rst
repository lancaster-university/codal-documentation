
.. _program_listing_file_libraries_codal-microbit-v2_source_compat_MicroBitI2C.cpp:

Program Listing for File MicroBitI2C.cpp
========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_compat_MicroBitI2C.cpp>` (``libraries/codal-microbit-v2/source/compat/MicroBitI2C.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   
   Copyright (c) 2020 Lancaster University.
   
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
   
   #include "MicroBitI2C.h"
   
   using namespace codal;
   
    MicroBitI2C::MicroBitI2C(NRF52Pin &sda, NRF52Pin &scl) : NRF52I2C(sda, scl) {
    }
   
    MicroBitI2C::MicroBitI2C(PinName sda, PinName scl) : NRF52I2C(*new NRF52Pin(sda, sda, PIN_CAPABILITY_ALL), *new NRF52Pin(scl, scl, PIN_CAPABILITY_ALL)) {
    }
   
    MicroBitI2C::MicroBitI2C(PinNumber sda, PinNumber scl) : NRF52I2C(*new NRF52Pin(sda, sda, PIN_CAPABILITY_ALL), *new NRF52Pin(scl, scl, PIN_CAPABILITY_ALL)) {
    }
