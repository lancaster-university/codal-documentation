
.. _program_listing_file_libraries_codal-microbit-v2_source_compat_MicroBitSerial.cpp:

Program Listing for File MicroBitSerial.cpp
===========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_compat_MicroBitSerial.cpp>` (``libraries/codal-microbit-v2/source/compat/MicroBitSerial.cpp``)

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
   
   #include "MicroBitSerial.h"
   
   using namespace codal;
   
   MicroBitSerial::MicroBitSerial(Pin& tx, Pin& rx, uint8_t rxBufferSize, uint8_t txBufferSize, uint16_t id) : NRF52Serial(tx, rx)
   {
   }
   
   MicroBitSerial::MicroBitSerial(PinName tx, PinName rx, uint8_t rxBufferSize, uint8_t txBufferSize, uint16_t id) : NRF52Serial(*new NRF52Pin(tx, tx, PIN_CAPABILITY_ALL), *new NRF52Pin(rx, rx, PIN_CAPABILITY_ALL))
   {
   }
   
   
   MicroBitSerial::MicroBitSerial(PinNumber tx, PinNumber rx, uint8_t rxBufferSize, uint8_t txBufferSize, uint16_t id) : NRF52Serial(*new NRF52Pin(tx, tx, PIN_CAPABILITY_ALL), *new NRF52Pin(rx, rx, PIN_CAPABILITY_ALL))
   {
   }
   
   int MicroBitSerial::redirect(PinName tx, PinName rx) {
       static Pin *oldRx = NULL;
       static Pin *oldTx = NULL;
   
       if (oldRx)
           delete oldRx;
   
       if (oldTx)
           delete oldTx;
   
       oldTx = new Pin(tx, tx, PIN_CAPABILITY_ALL);
       oldRx = new Pin(rx, rx, PIN_CAPABILITY_ALL);
   
       return Serial::redirect(*oldTx, *oldRx);
   }
   
   int MicroBitSerial::redirect(PinNumber tx, PinNumber rx) {
       static Pin *oldRx = NULL;
       static Pin *oldTx = NULL;
   
       if (oldRx)
           delete oldRx;
   
       if (oldTx)
           delete oldTx;
   
       oldTx = new Pin(tx, tx, PIN_CAPABILITY_ALL);
       oldRx = new Pin(rx, rx, PIN_CAPABILITY_ALL);
   
       return Serial::redirect(*oldTx, *oldRx);
   }
