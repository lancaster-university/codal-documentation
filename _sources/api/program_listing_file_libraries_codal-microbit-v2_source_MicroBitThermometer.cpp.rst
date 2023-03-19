
.. _program_listing_file_libraries_codal-microbit-v2_source_MicroBitThermometer.cpp:

Program Listing for File MicroBitThermometer.cpp
================================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_MicroBitThermometer.cpp>` (``libraries/codal-microbit-v2/source/MicroBitThermometer.cpp``)

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
   
   #include "MicroBitThermometer.h"
   #include "codal-core/inc/driver-models/Timer.h"
   #include "nrf.h"
   
   #ifdef SOFTDEVICE_PRESENT
   #include "MicroBitDevice.h"
   #include "nrf_soc.h"
   #include "nrf_sdm.h"
   #endif
   
   using namespace codal;
   
   /*
    * The underlying Nordic libraries that support BLE do not compile cleanly with the stringent GCC settings we employ
    * If we're compiling under GCC, then we suppress any warnings generated from this code (but not the rest of the DAL)
    * The ARM cc compiler is more tolerant. We don't test __GNUC__ here to detect GCC as ARMCC also typically sets this
    * as a compatability option, but does not support the options used...
    */
   
   MicroBitThermometer::MicroBitThermometer(uint16_t id)
   {
       this->id = id;
       this->samplePeriod = MICROBIT_THERMOMETER_PERIOD;
       this->sampleTime = 0;
       this->offset = 0;
       this->temperature = 0;
   }
   
   int MicroBitThermometer::getTemperature()
   {
       updateSample();
       return temperature - offset;
   }
   
   
   int MicroBitThermometer::updateSample()
   {
       // Ensure we're registered for a background processing callbacks.
       status |= DEVICE_COMPONENT_STATUS_IDLE_TICK;
   
       // check if we need to update our sample...
       if(isSampleNeeded())
       {
           int32_t processorTemperature = 0;
   
           // For now, we just rely on the nrf senesor to be the most accurate.
           // The compass module also has a temperature sensor, and has the lowest power consumption, so will run the cooler...
           // ...however it isn't trimmed for accuracy during manufacture, so requires calibration.
   
   #ifdef SOFTDEVICE_PRESENT
           if ( ble_running())
           {
               // If Bluetooth is enabled, we need to go through the Nordic software to safely do this
               sd_temp_get(&processorTemperature);
           }
           else
   #endif
           {
               // Othwerwise, we access the information directly...
               NRF_TEMP->TASKS_START = 1;
               while (NRF_TEMP->EVENTS_DATARDY == 0);
               NRF_TEMP->EVENTS_DATARDY = 0;
   
               processorTemperature = NRF_TEMP->TEMP;
   
               NRF_TEMP->TASKS_STOP = 1;
           }
   
   
           // Record our reading...
           temperature = processorTemperature / 4;
   
           // Schedule our next sample.
           sampleTime = system_timer_current_time() + samplePeriod;
   
           // Send an event to indicate that we'e updated our temperature.
           Event e(id, MICROBIT_THERMOMETER_EVT_UPDATE);
       }
   
       return DEVICE_OK;
   };
   
   void MicroBitThermometer::idleCallback()
   {
       updateSample();
   }
   
   int MicroBitThermometer::isSampleNeeded()
   {
       return  system_timer_current_time() >= sampleTime;
   }
   
   void MicroBitThermometer::setPeriod(int period)
   {
       updateSample();
       samplePeriod = period;
   }
   
   int MicroBitThermometer::getPeriod()
   {
       return samplePeriod;
   }
   
   int MicroBitThermometer::setCalibration(int offset)
   {
       this->offset = offset;
       return DEVICE_OK;
   }
   
   int MicroBitThermometer::getCalibration()
   {
       return offset;
   }
