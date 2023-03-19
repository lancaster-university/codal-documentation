
.. _program_listing_file_libraries_codal-core_source_driver-models_I2C.cpp:

Program Listing for File I2C.cpp
================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_I2C.cpp>` (``libraries/codal-core/source/driver-models/I2C.cpp``)

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
   
   #include "I2C.h"
   #include "ErrorNo.h"
   
   namespace codal
   {
       I2C::I2C(Pin &sda, Pin &scl)
       {
       }
   
       int I2C::redirect(Pin &sda, Pin &scl)
       {
           return DEVICE_NOT_IMPLEMENTED;
       }
   
       int I2C::setFrequency(uint32_t frequency)
       {
           return DEVICE_NOT_IMPLEMENTED;
       }
   
       int I2C::start()
       {
           return DEVICE_NOT_IMPLEMENTED;
       }
   
       int I2C::stop()
       {
           return DEVICE_NOT_IMPLEMENTED;
       }
   
       int I2C::write(uint8_t data)
       {
           return DEVICE_NOT_IMPLEMENTED;
       }
   
       int I2C::read(AcknowledgeType ack)
       {
           return DEVICE_NOT_IMPLEMENTED;
       }
   
       int I2C::write(uint16_t address, uint8_t data)
       {
           return write(address, &data, 1);
       }
   
       int I2C::write(uint16_t address, uint8_t *data, int len, bool repeated)
       {
           if (data == NULL || len <= 0)
               return DEVICE_INVALID_PARAMETER; // Send a start condition
   
           start();
   
           // Send the address of the slave, with a write bit set.
           write((uint8_t)address);
   
           // Send the body of the data
           for (int i = 0; i < len; i++)
               write(data[i]);
   
           // Send a stop condition
           if (!repeated)
               stop();
   
           return DEVICE_OK;
       }
   
       int I2C::writeRegister(uint16_t address, uint8_t reg, uint8_t value)
       {
           uint8_t command[2];
           command[0] = reg;
           command[1] = value;
   
           return write(address, command, 2);
       }
   
       int I2C::read(uint16_t address, uint8_t *data, int len, bool repeated)
       {
           int i = 0;
   
           if (data == NULL || len <= 0)
               return DEVICE_INVALID_PARAMETER;
   
           // Send a start condition
           start();
   
           // Send the address of the slave, with a read bit set.
           write((uint8_t)(address | 0x01));
   
           // Read the body of the data
           for (i = 0; i < len-1; i++)
               data[i] = read();
   
           data[i] = read(NACK);
   
           // Send a stop condition
           if (!repeated)
               stop();
   
           return DEVICE_OK;
       }
   
       int I2C::readRegister(uint16_t address, uint8_t reg, uint8_t *data, int length, bool repeated)
       {
           int result;
   
           if (repeated)
               result = write(address, &reg, 1, true);
           else
               result = write(address, reg);
   
           if (result != DEVICE_OK)
               return result;
   
           result = read(address, data, length);
           if (result != DEVICE_OK)
               return result;
   
           return DEVICE_OK;
       }
   
       int I2C::readRegister(uint8_t address, uint8_t reg)
       {
           int result;
           uint8_t data;
   
           result = readRegister(address, reg, &data, 1);
   
           return (result == DEVICE_OK) ? (int)data : result;
       }
   
       int I2C::write(int address, char *data, int len, bool repeated)
       {
           return write((uint16_t)address, (uint8_t *)data, len, repeated);
       }
   
       int I2C::read(int address, char *data, int len, bool repeated)
       {
           return read((uint16_t)address, (uint8_t *)data, len, repeated);
       }
   }
   
