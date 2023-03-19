
.. _program_listing_file_libraries_codal-core_source_drivers_ScreenIO.cpp:

Program Listing for File ScreenIO.cpp
=====================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_ScreenIO.cpp>` (``libraries/codal-core/source/drivers/ScreenIO.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #include "SPIScreenIO.h"
   
   namespace codal
   {
   
   SPIScreenIO::SPIScreenIO(SPI &spi) : spi(spi) {}
   
   void SPIScreenIO::send(const void *txBuffer, uint32_t txSize)
   {
       spi.transfer((const uint8_t *)txBuffer, txSize, NULL, 0);
   }
   
   void SPIScreenIO::startSend(const void *txBuffer, uint32_t txSize, PVoidCallback doneHandler,
                               void *handlerArg)
   {
       spi.startTransfer((const uint8_t *)txBuffer, txSize, NULL, 0, doneHandler, handlerArg);
   }
   
   } // namespace codal
