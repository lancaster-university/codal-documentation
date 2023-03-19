
.. _program_listing_file_libraries_codal-core_source_driver-models_Sensor.cpp:

Program Listing for File Sensor.cpp
===================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_Sensor.cpp>` (``libraries/codal-core/source/driver-models/Sensor.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   
   Copyright (c) 2017 Lancaster University.
   Copyright (c) 2018 Paul ADAM, inidinn.com
   
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
   
   #include "Sensor.h"
   #include "ErrorNo.h"
   #include "CodalCompat.h"
   #include "CodalFiber.h"
   #include "Timer.h"
   
   using namespace codal;
   
   Sensor::Sensor(uint16_t id, uint16_t sensitivity, uint16_t samplePeriod)
   {
       this->id = id;
       this->setSensitivity(sensitivity);
   
       // Configure for a 2 Hz update frequency by default.
       if(EventModel::defaultEventBus)
           EventModel::defaultEventBus->listen(this->id, SENSOR_UPDATE_NEEDED, this, &Sensor::onSampleEvent, MESSAGE_BUS_LISTENER_IMMEDIATE);
   
       this->setPeriod(samplePeriod);
   }
   
   /*
    * Event Handler for periodic sample timer
    */
   void Sensor::onSampleEvent(Event)
   {
       updateSample();
   }
   
   /*
    * Determines the instantaneous value of the sensor, in SI units, and returns it.
    *
    * @return The current value of the sensor.
    */
   int Sensor::getValue()
   {
       return (int)sensorValue;
   }
   
   void Sensor::updateSample()
   {
       uint32_t value = readValue();
   
       // If this is the first reading performed, take it a a baseline. Otherwise, perform a decay average to smooth out the data.
       if (!(this->status & SENSOR_INITIALISED))
       {
           sensorValue = (uint16_t)value;
           this->status |=  SENSOR_INITIALISED;
       }
       else
       {
           sensorValue = ((sensorValue * (1023 - sensitivity)) + (value * sensitivity)) >> 10;
       }
   
       checkThresholding();
   }
   
   void Sensor::checkThresholding()
   {
       if ((this->status & SENSOR_HIGH_THRESHOLD_ENABLED) && (!(this->status & SENSOR_HIGH_THRESHOLD_PASSED)) && (sensorValue >= highThreshold))
       {
           Event(this->id, SENSOR_THRESHOLD_HIGH);
           this->status |=  SENSOR_HIGH_THRESHOLD_PASSED;
           this->status &= ~SENSOR_LOW_THRESHOLD_PASSED;
       }
   
       if ((this->status & SENSOR_LOW_THRESHOLD_ENABLED) && (!(this->status & SENSOR_LOW_THRESHOLD_PASSED)) && (sensorValue <= lowThreshold))
   
       {
           Event(this->id, SENSOR_THRESHOLD_LOW);
           this->status |=  SENSOR_LOW_THRESHOLD_PASSED;
           this->status &= ~SENSOR_HIGH_THRESHOLD_PASSED;
       }
   }
   
   int Sensor::setSensitivity(uint16_t value)
   {
       this->sensitivity = max(0, min(1023, value));
   
       return DEVICE_OK;
   }
   
   int Sensor::setPeriod(int period)
   {
       this->samplePeriod = period > 0 ? period : SENSOR_DEFAULT_SAMPLE_PERIOD;
       system_timer_event_every(this->samplePeriod, this->id, SENSOR_UPDATE_NEEDED);
   
       return DEVICE_OK;
   }
   
   int Sensor::getPeriod()
   {
       return samplePeriod;
   }
   
   int Sensor::setLowThreshold(uint16_t value)
   {
       // Protect against churn if the same threshold is set repeatedly.
       if ((this->status & SENSOR_LOW_THRESHOLD_ENABLED) && lowThreshold == value)
           return DEVICE_OK;
   
       // We need to update our threshold
       lowThreshold = value;
   
       // Reset any exisiting threshold state, and enable threshold detection.
       this->status &= ~SENSOR_LOW_THRESHOLD_PASSED;
       this->status |=  SENSOR_LOW_THRESHOLD_ENABLED;
   
       // If a HIGH threshold has been set, ensure it's above the LOW threshold.
       if(this->status & SENSOR_HIGH_THRESHOLD_ENABLED)
           setHighThreshold(max(lowThreshold+1, highThreshold));
   
       return DEVICE_OK;
   }
   
   int Sensor::setHighThreshold(uint16_t value)
   {
       // Protect against churn if the same threshold is set repeatedly.
       if ((this->status & SENSOR_HIGH_THRESHOLD_ENABLED) && highThreshold == value)
           return DEVICE_OK;
   
       // We need to update our threshold
       highThreshold = value;
   
       // Reset any exisiting threshold state, and enable threshold detection.
       this->status &= ~SENSOR_HIGH_THRESHOLD_PASSED;
       this->status |=  SENSOR_HIGH_THRESHOLD_ENABLED;
   
       // If a HIGH threshold has been set, ensure it's above the LOW threshold.
       if(this->status & SENSOR_LOW_THRESHOLD_ENABLED)
           setLowThreshold(min(highThreshold - 1, lowThreshold));
   
       return DEVICE_OK;
   }
   
   int Sensor::getLowThreshold()
   {
       if (!(this->status & SENSOR_LOW_THRESHOLD_ENABLED))
           return DEVICE_INVALID_PARAMETER;
   
       return lowThreshold;
   }
   
   int Sensor::getHighThreshold()
   {
       if (!(this->status & SENSOR_HIGH_THRESHOLD_ENABLED))
           return DEVICE_INVALID_PARAMETER;
   
       return highThreshold;
   }
   
   Sensor::~Sensor()
   {
   }
