
.. _program_listing_file_libraries_codal-core_source_drivers_LSM303Magnetometer.cpp:

Program Listing for File LSM303Magnetometer.cpp
===============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_LSM303Magnetometer.cpp>` (``libraries/codal-core/source/drivers/LSM303Magnetometer.cpp``)

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
   #include "CodalComponent.h"
   #include "CodalDmesg.h"
   #include "CodalUtil.h"
   #include "CoordinateSystem.h"
   #include "LSM303Magnetometer.h"
   #include "Compass.h"
   #include "ErrorNo.h"
   #include "Event.h"
   
   using namespace codal;
   
   //
   // Configuration table for available data update frequency.
   // maps microsecond period -> LSM303_CFG_REG_A_M data rate selection bits [2..3]
   //
   static const KeyValueTableEntry magnetometerPeriodData[] = {
       {10000, 0x0C},             // 100 Hz
       {20000, 0x08},             // 50 Hz
       {50000, 0x04},             // 20 Hz
       {100000, 0x00}             // 10 Hz
   };
   CREATE_KEY_VALUE_TABLE(magnetometerPeriod, magnetometerPeriodData);
   
   
   int LSM303Magnetometer::configure()
   {
       int result;
       uint8_t value;
   
       // First find the nearest sample rate to that specified.
       samplePeriod = magnetometerPeriod.getKey(samplePeriod * 1000) / 1000;
   
       // Now configure the magnetometer for the requested sample rate, low power continuous mode with temperature compensation disabled
       value = magnetometerPeriod.get(samplePeriod * 1000);
   
       // Configure the component as enabled or disabled as appropriate.
       if (!(status & LSM303_M_STATUS_ENABLED))
           value |= 0x03;
   
       result = i2c.writeRegister(address, LSM303_CFG_REG_A_M, value);
       if (result != DEVICE_OK)
       {
           DMESG("LSM303 INIT: ERROR WRITING LSM303_CFG_REG_A_M");
           return DEVICE_I2C_ERROR;
       }
   
       // Enable Data Ready interrupt, with buffering of data to avoid race conditions.
       value = status & LSM303_M_STATUS_ENABLED ? 0x01 : 0x00;
       result = i2c.writeRegister(address, LSM303_CFG_REG_C_M, value);
       if (result != DEVICE_OK)
       {
           DMESG("LSM303 INIT: ERROR WRITING LSM303_CFG_REG_C_M");
           return DEVICE_I2C_ERROR;
       }
   
       return DEVICE_OK;
   }
   
   LSM303Magnetometer::LSM303Magnetometer(I2C &_i2c, Pin &_int1, CoordinateSpace &coordinateSpace, uint16_t address, uint16_t id) : Compass(coordinateSpace, id), i2c(_i2c), int1(_int1)
   {
       // Store our identifiers.
       this->address = address;
   
       // Configure and enable the magnetometer.
       configure();
   }
   
   
   int LSM303Magnetometer::requestUpdate()
   {
       bool awaitSample = false;
   
       if ((status & LSM303_M_STATUS_ENABLED) == 0x00)
       {
           // If we get here without being enabled, applicaiton code has requested
           // functionlity from this component. Perform on demand activation.
           status |= LSM303_M_STATUS_ENABLED;
           status |= DEVICE_COMPONENT_STATUS_IDLE_TICK;
           configure();
   
           // Ensure the first sample is accurate.
           awaitSample = true;
       }   
   
       // Poll interrupt line from device 
       do{
           if(int1.isActive())
           {
               uint8_t data[6];
               int result;
               int16_t *x;
               int16_t *y;
               int16_t *z;
   
       #if CONFIG_ENABLED(DEVICE_I2C_IRQ_SHARED)
               // Determine if this device has all its data ready (we may be on a shared IRQ line)
               uint8_t status_reg = i2c.readRegister(address, LSM303_STATUS_REG_M);
               if((status_reg & LSM303_M_STATUS_DATA_READY) != LSM303_M_STATUS_DATA_READY)
               {
                   if (awaitSample)
                       continue;
                   else
                       return DEVICE_OK;
               }
       #endif
   
               // Read the combined accelerometer and magnetometer data.
               result = i2c.readRegister(address, LSM303_OUTX_L_REG_M | 0x80, data, 6);
               awaitSample = false;
   
               if (result !=0)
                   return DEVICE_I2C_ERROR;
   
               // Read in each reading as a 16 bit little endian value, and scale to 10 bits.
               x = ((int16_t *) &data[0]);
               y = ((int16_t *) &data[2]);
               z = ((int16_t *) &data[4]);
   
               // Align to ENU coordinate system
               sampleENU.x = LSM303_M_NORMALIZE_SAMPLE(-((int)(*y)));
               sampleENU.y = LSM303_M_NORMALIZE_SAMPLE(-((int)(*x)));
               sampleENU.z = LSM303_M_NORMALIZE_SAMPLE(((int)(*z)));
   
               // indicate that new data is available.
               update();
           }
       } while (awaitSample);
   
       return DEVICE_OK;
   }
   
   
   void LSM303Magnetometer::idleCallback()
   {
       requestUpdate();
   }
   
   int LSM303Magnetometer::setSleep(bool doSleep)
   {
       if (doSleep && (status & LSM303_M_STATUS_ENABLED))
       {
           status &= ~DEVICE_COMPONENT_STATUS_IDLE_TICK;
           status |= LSM303_M_STATUS_SLEEPING;
           status &= ~LSM303_M_STATUS_ENABLED;
           configure();
       }
       
       if (!doSleep && (status & LSM303_M_STATUS_SLEEPING))
       {
           status |= DEVICE_COMPONENT_STATUS_IDLE_TICK;
           status &= ~LSM303_M_STATUS_SLEEPING;
       }
      
       return DEVICE_OK;
   }
   
   int LSM303Magnetometer::isDetected(I2C &i2c, uint16_t address)
   {
       return i2c.readRegister(address, LSM303_WHO_AM_I_M) == LSM303_M_WHOAMI_VAL;
   }
   
   LSM303Magnetometer::~LSM303Magnetometer()
   {
   }
   
