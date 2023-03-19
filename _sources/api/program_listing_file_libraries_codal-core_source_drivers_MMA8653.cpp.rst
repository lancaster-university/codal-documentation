
.. _program_listing_file_libraries_codal-core_source_drivers_MMA8653.cpp:

Program Listing for File MMA8653.cpp
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_MMA8653.cpp>` (``libraries/codal-core/source/drivers/MMA8653.cpp``)

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
   #include "CodalComponent.h"
   #include "MMA8653.h"
   #include "ErrorNo.h"
   
   using namespace codal;
   int MMA8653::configure()
   {
       const MMA8653SampleRangeConfig  *actualSampleRange;
       const MMA8653SampleRateConfig  *actualSampleRate;
       int result;
   
       // First find the nearest sample rate to that specified.
       actualSampleRate = &MMA8653SampleRate[MMA8653_SAMPLE_RATES-1];
       for (int i=MMA8653_SAMPLE_RATES-1; i>=0; i--)
       {
           if(MMA8653SampleRate[i].sample_period < this->samplePeriod * 1000)
               break;
   
           actualSampleRate = &MMA8653SampleRate[i];
       }
   
       // Now find the nearest sample range to that specified.
       actualSampleRange = &MMA8653SampleRange[MMA8653_SAMPLE_RANGES-1];
       for (int i=MMA8653_SAMPLE_RANGES-1; i>=0; i--)
       {
           if(MMA8653SampleRange[i].sample_range < this->sampleRange)
               break;
   
           actualSampleRange = &MMA8653SampleRange[i];
       }
   
       // OK, we have the correct data. Update our local state.
       this->samplePeriod = actualSampleRate->sample_period / 1000;
       this->sampleRange = actualSampleRange->sample_range;
   
       // Now configure the accelerometer accordingly.
       // First place the device into standby mode, so it can be configured.
       result = i2c.writeRegister(this->address, MMA8653_CTRL_REG1, 0x00);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       // Enable high precisiosn mode. This consumes a bit more power, but still only 184 uA!
       result = i2c.writeRegister(this->address, MMA8653_CTRL_REG2, 0x10);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       // Enable the INT1 interrupt pin.
       result = i2c.writeRegister(this->address, MMA8653_CTRL_REG4, 0x01);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       // Select the DATA_READY event source to be routed to INT1
       result = i2c.writeRegister(this->address, MMA8653_CTRL_REG5, 0x01);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       // Configure for the selected g range.
       result = i2c.writeRegister(this->address, MMA8653_XYZ_DATA_CFG, actualSampleRange->xyz_data_cfg);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       // Bring the device back online, with 10bit wide samples at the requested frequency.
       result = i2c.writeRegister(this->address, MMA8653_CTRL_REG1, actualSampleRate->ctrl_reg1 | 0x01);
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       return DEVICE_OK;
   }
   
   MMA8653::MMA8653(I2C& _i2c, Pin& int1, CoordinateSpace& cspace, uint16_t address, uint16_t id) : Accelerometer(cspace, id), int1(int1), i2c(_i2c)
   {
       this->address = address;
   
       // Configure and enable the accelerometer.
       if (configure() == DEVICE_OK)
           status |= (DEVICE_COMPONENT_RUNNING);
   }
   
   int MMA8653::whoAmI()
   {
       uint8_t data;
       int result;
   
       result = i2c.readRegister(this->address, MMA8653_WHOAMI, &data, 1);
   
       if (result != DEVICE_OK)
           return DEVICE_I2C_ERROR;
   
       return (int)data;
   }
   
   int MMA8653::requestUpdate()
   {
       if(!(status & DEVICE_COMPONENT_STATUS_IDLE_TICK))
           status |= DEVICE_COMPONENT_STATUS_IDLE_TICK;
   
       // Poll interrupt line from accelerometer.
       // n.b. Default is Active LO. Interrupt is cleared in data read.
       if(!int1.getDigitalValue())
       {
           Sample3D s;
           int8_t data[6];
           int result;
   
           result = i2c.readRegister(this->address, MMA8653_OUT_X_MSB, (uint8_t *)data, 6);
           if (result != DEVICE_OK)
               return DEVICE_I2C_ERROR;
   
           // read MSB values...
           sampleENU.x = data[0];
           sampleENU.y = data[2];
           sampleENU.z = data[4];
   
           // Normalize the data in the 0..1024 range.
           sampleENU.x *= 8;
           sampleENU.y *= 8;
           sampleENU.z *= 8;
   
   #if CONFIG_ENABLED(USE_ACCEL_LSB)
           // Add in LSB values.
           sampleENU.x += (data[1] / 64);
           sampleENU.y += (data[3] / 64);
           sampleENU.z += (data[5] / 64);
   #endif
   
           // Scale into millig (approx!)
           sampleENU.x *= this->sampleRange;
           sampleENU.y *= this->sampleRange;
           sampleENU.z *= this->sampleRange;
   
           update();
       }
   
       return DEVICE_OK;
   };
   
   void MMA8653::idleCallback()
   {
       requestUpdate();
   }
   
   int MMA8653::setSleep(bool sleepMode)
   {
       if (sleepMode)
           return i2c.writeRegister(this->address, MMA8653_CTRL_REG1, 0x00);
       else
           return configure();
   }
   
   
   const MMA8653SampleRangeConfig MMA8653SampleRange[MMA8653_SAMPLE_RANGES] = {
       {2, 0},
       {4, 1},
       {8, 2}
   };
   
   const MMA8653SampleRateConfig MMA8653SampleRate[MMA8653_SAMPLE_RATES] = {
       {1250,      0x00},
       {2500,      0x08},
       {5000,      0x10},
       {10000,     0x18},
       {20000,     0x20},
       {80000,     0x28},
       {160000,    0x30},
       {640000,    0x38}
   };
