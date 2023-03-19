
.. _program_listing_file_libraries_codal-core_source_driver-models_PinPeripheral.cpp:

Program Listing for File PinPeripheral.cpp
==========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_PinPeripheral.cpp>` (``libraries/codal-core/source/driver-models/PinPeripheral.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   
   Copyright (c) 2022 Lancaster University.
   
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
   
   #include "Pin.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   int PinPeripheral::releasePin(Pin &pin)
   {
       return DEVICE_NOT_IMPLEMENTED;
   }
   
   bool PinPeripheral::isPinLocked()
   {
       return pinLock;
   }
   
   void PinPeripheral::setPinLock(bool locked)
   {
       pinLock = locked;
   }
   
   int PinPeripheral::reassignPin(void *p, Pin *newPin)
   {
       Pin **pin = (Pin **)p;
   
       if (pin == NULL)
           return DEVICE_INVALID_PARAMETER;
   
       // If the pin is changing state, reelase any old peripherals and attach the new one.
       if (*pin != newPin)
       {
           if (*pin)
               (*pin)->disconnect();
   
           if (newPin)
               newPin->connect(*this);
   
           *pin = newPin;
       }
   
       return DEVICE_OK;
   }
   
