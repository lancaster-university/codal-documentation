
.. _program_listing_file_libraries_codal-core_source_drivers_LIS3DH.cpp:

Program Listing for File LIS3DH.cpp
===================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_LIS3DH.cpp>` (``libraries/codal-core/source/drivers/LIS3DH.cpp``)

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
   
   #include "CodalConfig.h"
   #include "LIS3DH.h"
   #include "ErrorNo.h"
   #include "CodalCompat.h"
   #include "CodalFiber.h"
   
   using namespace codal;
   
   //
   // Configuration table for available g force ranges.
   // Maps g -> LIS3DH_CTRL_REG4 [5..4]
   //
   static const KeyValueTableEntry accelerometerRangeData[] = {
       {2, 0},
       {4, 1},
       {8, 2},
       {16, 3}
   };
   CREATE_KEY_VALUE_TABLE(accelerometerRange, accelerometerRangeData);
   
   //
   // Configuration table for available data update frequency.
   // maps microsecond period -> LIS3DH_CTRL_REG1 data rate selection bits
   //
   static const KeyValueTableEntry accelerometerPeriodData[] = {
       {2500,      0x70},
       {5000,      0x60},
       {10000,     0x50},
       {20000,     0x40},
       {40000,     0x30},
       {100000,    0x20},
       {1000000,   0x10}
   };
   CREATE_KEY_VALUE_TABLE(accelerometerPeriod, accelerometerPeriodData);
   
   LIS3DH::LIS3DH(I2C& _i2c, Pin &_int1, CoordinateSpace &coordinateSpace, uint16_t address,  uint16_t id) : Accelerometer(coordinateSpace, id), i2c(_i2c), int1(_int1)
   {
       // Store our identifiers.
       this->id = id;
       this->status = 0;
       this->address = address;
   
       // Configure and enable the accelerometer.
       configure();
   }
   
   int LIS3DH::configure()
   {
       int result;
       uint8_t value;
   
       // First find the nearest sample rate to that specified.
       samplePeriod = accelerometerPeriod.getKey(samplePeriod * 1000) / 1000;
       sampleRange = accelerometerRange.getKey(sampleRange);
   
       // Now configure the accelerometer accordingly.
       // Firstly, Configure for normal precision operation at the sample rate requested.
       value = accelerometerPeriod.get(samplePeriod * 1000) | 0x07;
       result = i2c.writeRegister(address, LIS3DH_CTRL_REG1, value);
       if (result != 0)
           return DEVICE_I2C_ERROR;
   
       // Enable the INT1 interrupt pin when XYZ data is available.
       value = 0x10;
       result = i2c.writeRegister(address, LIS3DH_CTRL_REG3, value);
       if (result != 0)
           return DEVICE_I2C_ERROR;
   
       // Configure for the selected g range.
       value = accelerometerRange.get(sampleRange) << 4;
       result = i2c.writeRegister(address, LIS3DH_CTRL_REG4,  value);
       if (result != 0)
           return DEVICE_I2C_ERROR;
   
       // Configure for a latched interrupt request.
       value = 0x08;
       result = i2c.writeRegister(address, LIS3DH_CTRL_REG5, value);
       if (result != 0)
           return DEVICE_I2C_ERROR;
   
       return DEVICE_OK;
   }
   
   
   int LIS3DH::whoAmI()
   {
       uint8_t data;
       int result;
   
       result = i2c.readRegister(address, LIS3DH_WHOAMI, &data, 1);
       if (result !=0)
           return DEVICE_I2C_ERROR;
   
       return (int)data;
   }
   
   int LIS3DH::requestUpdate()
   {
       // Ensure we're scheduled to update the data periodically
       status |= DEVICE_COMPONENT_STATUS_IDLE_TICK;
   
       // Poll interrupt line from accelerometer.
       if(int1.getDigitalValue() == 1)
       {
           int8_t data[6];
           uint8_t src;
           int result;
   
           // read the XYZ data (16 bit)
           // n.b. we need to set the MSB bit to enable multibyte transfers from this device (WHY? Who Knows!)
           result = i2c.readRegister(address, 0x80 | LIS3DH_OUT_X_L, (uint8_t *)data, 6);
   
           if (result !=0)
               return DEVICE_I2C_ERROR;
   
           target_wait_us(3);
   
           // Acknowledge the interrupt.
           i2c.readRegister(address, LIS3DH_INT1_SRC, &src, 1);
   
           // read MSB values...
           sampleENU.x = data[1];
           sampleENU.y = data[3];
           sampleENU.z = data[5];
   
           // Normalize the data in the 0..1024 range.
           sampleENU.x *= 8;
           sampleENU.y *= 8;
           sampleENU.z *= 8;
   
   #if CONFIG_ENABLED(USE_ACCEL_LSB)
           // Add in LSB values.
           sampleENU.x += (data[0] / 64);
           sampleENU.y += (data[2] / 64);
           sampleENU.z += (data[4] / 64);
   #endif
   
           // Scale into millig (approx!). (LIS3DH is ENU aligned)
           sampleENU.x *= this->sampleRange;
           sampleENU.y *= this->sampleRange;
           sampleENU.z *= this->sampleRange;
    
           // Indicate that a new sample is available
           update();
       }
   
       return DEVICE_OK;
   };
   
   
   void LIS3DH::idleCallback()
   {
       requestUpdate();
   }
   
   LIS3DH::~LIS3DH()
   {
   }
   
   int LIS3DH::setSleep(bool sleepMode)
   {
       if (sleepMode)
           return i2c.writeRegister(this->address, LIS3DH_CTRL_REG1, 0x00);
       else
           return configure();
   }
