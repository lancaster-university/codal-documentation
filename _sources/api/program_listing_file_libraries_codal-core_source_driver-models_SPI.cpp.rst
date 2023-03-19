
.. _program_listing_file_libraries_codal-core_source_driver-models_SPI.cpp:

Program Listing for File SPI.cpp
================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_SPI.cpp>` (``libraries/codal-core/source/driver-models/SPI.cpp``)

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
   
   #include "SPI.h"
   #include "ErrorNo.h"
   #include "CodalFiber.h"
   
   namespace codal
   {
   
   int SPI::redirect(Pin &mosi, Pin &miso, Pin &sclk)
   {
       return DEVICE_NOT_IMPLEMENTED;
   }
   
   int SPI::transfer(const uint8_t *txBuffer, uint32_t txSize, uint8_t *rxBuffer, uint32_t rxSize)
   {
       uint32_t len = txSize;
       if (rxSize > len)
           len = rxSize;
       for (uint32_t i = 0; i < len; ++i)
       {
           int c = write(i < txSize ? txBuffer[i] : 0);
           if (c < 0)
               return DEVICE_SPI_ERROR;
           if (i < rxSize)
               rxBuffer[i] = c;
       }
       return DEVICE_OK;
   }
   
   int SPI::startTransfer(const uint8_t *txBuffer, uint32_t txSize, uint8_t *rxBuffer, uint32_t rxSize,
                          PVoidCallback doneHandler, void *arg)
   {
       int r = transfer(txBuffer, txSize, rxBuffer, rxSize);
       // it's important this doesn't get invoked recursievely, since that leads to stack overflow
       create_fiber(doneHandler, arg);
       return r;
   }
   }
