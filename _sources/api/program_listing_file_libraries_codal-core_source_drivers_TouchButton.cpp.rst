
.. _program_listing_file_libraries_codal-core_source_drivers_TouchButton.cpp:

Program Listing for File TouchButton.cpp
========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_TouchButton.cpp>` (``libraries/codal-core/source/drivers/TouchButton.cpp``)

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
   #include "CodalDmesg.h"
   #include "TouchButton.h"
   #include "Timer.h"
   #include "EventModel.h"
   
   using namespace codal;
   
   TouchButton::TouchButton(Pin &pin, TouchSensor &sensor, int threshold) : Button(pin, pin.id, DEVICE_BUTTON_ALL_EVENTS, ACTIVE_LOW, PullMode::None), touchSensor(sensor)
   {
       // Disable periodic events. These will come from our TouchSensor.
       this->threshold = threshold;
       this->reading = 0;
   
       // register ourselves with the sensor
       touchSensor.addTouchButton(this);
   
       // Perform a calibraiton if necessary
       if (threshold < 0)
           calibrate();
   }
   
   int TouchButton::buttonActive()
   {
       if (status & TOUCH_BUTTON_CALIBRATING)
           return 0;
   
       return reading >= threshold;
   }
   
   void TouchButton::calibrate()
   {
       // indicate that we're entering a calibration phase.
       // We reuse the threshold variable to track calibration progress, just to save a little memory.
       this->reading = TOUCH_BUTTON_CALIBRATION_PERIOD;
       threshold = 0;
       status |= TOUCH_BUTTON_CALIBRATING;
   }
   
   void TouchButton::setThreshold(int threshold)
   {
       this->threshold = threshold;
   }
   
   int TouchButton::getThreshold()
   {
       return this->threshold;
   }
   
   int TouchButton::getPinValue()
   {
       int result;
   
       setPinLock(true);
       result = _pin.getDigitalValue();
       setPinLock(false);
   
       return result;
   }
   
   void TouchButton::setPinValue(int v)
   {
       setPinLock(true);
       _pin.setDigitalValue(v);
       setPinLock(false);
   }
   
   int TouchButton::getValue()
   {
       return reading;
   }
   
   void TouchButton::setValue(int reading)
   {
       if (status & TOUCH_BUTTON_CALIBRATING)
       {
           // if this is the first reading, take it as our best estimate
           if (threshold == 0)
               this->threshold = reading;
   
           // Record the highest value measured. This is our baseline.
           this->threshold = max(this->threshold, reading);
   
   #ifdef TOUCH_BUTTON_DECAY_AVERAGE
           this->threshold = ((this->threshold * (100-TOUCH_BUTTON_DECAY_AVERAGE)) / 100) + ((reading * TOUCH_BUTTON_DECAY_AVERAGE) / 100);
   #endif
           this->reading--;
   
           // We've completed calibration, return to normal mode of operation.
           if (this->reading == 0)
           {
               this->threshold += ((this->threshold * TOUCH_BUTTON_SENSITIVITY) / 100) + TOUCH_BUTTON_CALIBRATION_LINEAR_OFFSET;
               status &= ~TOUCH_BUTTON_CALIBRATING;
           }
   
           return;
       }
   
       // Otherewise we're not calibrating, so simply record the result.
       this->reading = reading;
   #ifdef TOUCH_BUTTON_DECAY_AVERAGE
       this->reading = ((this->reading * (100-TOUCH_BUTTON_DECAY_AVERAGE)) / 100) + ((reading * TOUCH_BUTTON_DECAY_AVERAGE) / 100);
   #endif
   }
   
   
   TouchButton::~TouchButton()
   {
       touchSensor.removeTouchButton(this);
   }
