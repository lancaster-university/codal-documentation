
.. _program_listing_file_libraries_codal-core_source_drivers_MAG3110.cpp:

Program Listing for File MAG3110.cpp
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_MAG3110.cpp>` (``libraries/codal-core/source/drivers/MAG3110.cpp``)

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
   
   #include "CodalConfig.h"
   #include "MAG3110.h"
   #include "ErrorNo.h"
   #include "I2C.h"
   #include "CodalFiber.h"
   
   using namespace codal;
   
   MAG3110::MAG3110(I2C& _i2c, Pin& int1, Accelerometer& _accelerometer, CoordinateSpace &coordinateSpace, uint16_t address, uint16_t id) :
       Compass(_accelerometer, coordinateSpace, id),
       int1(int1),
       i2c(_i2c)
   {
       this->address = address;
   
       // Select 10Hz update rate, with oversampling, and enable the device.
       this->samplePeriod = 100;
       this->configure();
   
       // Indicate that we're up and running.
       status |= (DEVICE_COMPONENT_RUNNING);
   }
   
   int MAG3110::whoAmI()
   {
       uint8_t data;
       int result;
   
       result = i2c.readRegister(address, MAG_WHOAMI, &data, 1);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       return (int)data;
   }
   
   int MAG3110::requestUpdate()
   {
       if(!(status & DEVICE_COMPONENT_STATUS_IDLE_TICK))
           status |= DEVICE_COMPONENT_STATUS_IDLE_TICK;
   
       // Poll interrupt line from compass (Active HI).
       // Interrupt is cleared on data read of MAG_OUT_X_MSB.
       if(int1.getDigitalValue())
       {
           uint8_t data[6];
           int16_t s;
           uint8_t *lsb = (uint8_t *) &s;
           uint8_t *msb = lsb + 1;
           int result;
   
           // Read the combined magnetometer and magnetometer data.
           result = i2c.readRegister(address, MAG_OUT_X_MSB, data, 6);
   
           if (result !=0)
               return DEVICE_I2C_ERROR;
               
           // Scale the 14 bit data (packed into 16 bits) into SI units (milli-g) and translate into signed little endian, and align to ENU coordinate system
           *msb = data[0];
           *lsb = data[1];
           sampleENU.y = MAG3110_NORMALIZE_SAMPLE(s); 
   
           *msb = data[2];
           *lsb = data[3];
           sampleENU.x = -MAG3110_NORMALIZE_SAMPLE(s); 
   
           *msb = data[4];
           *lsb = data[5];
           sampleENU.z = -MAG3110_NORMALIZE_SAMPLE(s); 
   
           // Inform the higher level driver that raw data has been updated.
           update();
    
       }
   
       return DEVICE_OK;
   }
   
   void MAG3110::idleCallback()
   {
       requestUpdate();
   }
   
   int MAG3110::configure()
   {
       const MAG3110SampleRateConfig  *actualSampleRate;
       int result;
   
       // First, take the device offline, so it can be configured.
       result = i2c.writeRegister(this->address,MAG_CTRL_REG1, 0x00);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       // Wait for the part to enter standby mode...
       while(1)
       {
           // Read the status of the part...
           // If we can't communicate with it over I2C, pass on the error.
           uint8_t d = 0;
           result = i2c.readRegister(this->address, MAG_SYSMOD, &d, 1);
           if (result == DEVICE_I2C_ERROR)
               return DEVICE_I2C_ERROR;
   
           // if the part in in standby, we're good to carry on.
           if(result == 0)
               break;
   
           // Perform a power efficient sleep...
           fiber_sleep(100);
       }
   
       // Find the nearest sample rate to that specified.
       actualSampleRate = &MAG3110SampleRate[MAG3110_SAMPLE_RATES-1];
       for (int i=MAG3110_SAMPLE_RATES-1; i>=0; i--)
       {
           if(MAG3110SampleRate[i].sample_period < this->samplePeriod * 1000)
               break;
   
           actualSampleRate = &MAG3110SampleRate[i];
       }
   
       // OK, we have the correct data. Update our local state.
       this->samplePeriod = actualSampleRate->sample_period / 1000;
   
       // Enable automatic reset after each sample;
       result = i2c.writeRegister(this->address, MAG_CTRL_REG2, 0xA0);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
   
       // Bring the device online, with the requested sample frequency.
       result = i2c.writeRegister(this->address, MAG_CTRL_REG1, actualSampleRate->ctrl_reg1 | 0x01);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       return DEVICE_OK;
   }
   
   const MAG3110SampleRateConfig MAG3110SampleRate[MAG3110_SAMPLE_RATES] = {
       {12500,      0x00},        // 80 Hz
       {25000,      0x20},        // 40 Hz
       {50000,      0x40},        // 20 Hz
       {100000,     0x60},        // 10 hz
       {200000,     0x80},        // 5 hz
       {400000,     0x88},        // 2.5 hz
       {800000,     0x90},        // 1.25 hz
       {1600000,    0xb0},        // 0.63 hz
       {3200000,    0xd0},        // 0.31 hz
       {6400000,    0xf0},        // 0.16 hz
       {12800000,   0xf8}         // 0.08 hz
   };
