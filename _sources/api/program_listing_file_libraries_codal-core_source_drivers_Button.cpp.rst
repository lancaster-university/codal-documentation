
.. _program_listing_file_libraries_codal-core_source_drivers_Button.cpp:

Program Listing for File Button.cpp
===================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_Button.cpp>` (``libraries/codal-core/source/drivers/Button.cpp``)

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
   #include "Button.h"
   #include "Timer.h"
   #include "EventModel.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   Button::Button(Pin &pin, uint16_t id, ButtonEventConfiguration eventConfiguration, ButtonPolarity polarity, PullMode mode) : _pin(pin)
   {
       this->id = id;
       this->eventConfiguration = eventConfiguration;
       this->downStartTime = 0;
       this->sigma = 0;
       this->polarity = polarity;
   
       pin.setPolarity( polarity == ACTIVE_HIGH ? 1 : 0);
       pin.setPull(mode);
   
       this->status |= DEVICE_COMPONENT_STATUS_SYSTEM_TICK;
   }
   
   void Button::setEventConfiguration(ButtonEventConfiguration config)
   {
       this->eventConfiguration = config;
   }
   
   int Button::buttonActive()
   {
       bool active;
   
       setPinLock(true);
       active = _pin.getDigitalValue() == polarity;
       setPinLock(false);
   
       return active;
   }
   
   void Button::periodicCallback()
   {
       // If this button is disabled, do nothing.
       if (!(status & DEVICE_COMPONENT_RUNNING))
           return;
   
       //
       // If the pin is pulled low (touched), increment our culumative counter.
       // otherwise, decrement it. We're essentially building a lazy follower here.
       // This makes the output debounced for buttons, and desensitizes touch sensors
       // (particularly in environments where there is mains noise!)
       //
       if(buttonActive())
       {
           if (sigma < DEVICE_BUTTON_SIGMA_MAX)
               sigma++;
       }
       else
       {
           if (sigma > DEVICE_BUTTON_SIGMA_MIN)
               sigma--;
       }
   
       // Check to see if we have off->on state change.
       if(sigma > DEVICE_BUTTON_SIGMA_THRESH_HI && !(status & DEVICE_BUTTON_STATE))
       {
           // Record we have a state change, and raise an event.
           status |= DEVICE_BUTTON_STATE;
           Event evt(id,DEVICE_BUTTON_EVT_DOWN);
           clickCount++;
   
           //Record the time the button was pressed.
           downStartTime = system_timer_current_time();
       }
   
       // Check to see if we have on->off state change.
       if(sigma < DEVICE_BUTTON_SIGMA_THRESH_LO && (status & DEVICE_BUTTON_STATE))
       {
           status &= ~DEVICE_BUTTON_STATE;
           status &= ~DEVICE_BUTTON_STATE_HOLD_TRIGGERED;
           Event evt(id,DEVICE_BUTTON_EVT_UP);
   
          if (eventConfiguration == DEVICE_BUTTON_ALL_EVENTS)
          {
              //determine if this is a long click or a normal click and send event
              if((system_timer_current_time() - downStartTime) >= DEVICE_BUTTON_LONG_CLICK_TIME)
                  Event evt(id,DEVICE_BUTTON_EVT_LONG_CLICK);
              else
                  Event evt(id,DEVICE_BUTTON_EVT_CLICK);
          }
       }
   
       //if button is pressed and the hold triggered event state is not triggered AND we are greater than the button debounce value
       if((status & DEVICE_BUTTON_STATE) && !(status & DEVICE_BUTTON_STATE_HOLD_TRIGGERED) && (system_timer_current_time() - downStartTime) >= DEVICE_BUTTON_HOLD_TIME)
       {
           //set the hold triggered event flag
           status |= DEVICE_BUTTON_STATE_HOLD_TRIGGERED;
   
           //fire hold event
           Event evt(id,DEVICE_BUTTON_EVT_HOLD);
       }
   }
   
   int Button::isPressed()
   {
       return status & DEVICE_BUTTON_STATE ? 1 : 0;
   }
   
   int Button::releasePin(Pin &pin)
   {
       // We've been asked to disconnect from the given pin.
       // Stop requesting periodic callbacks from the scheduler.
       this->status &= ~DEVICE_COMPONENT_STATUS_SYSTEM_TICK;
   
       if (deleteOnRelease)
           delete this;
   
       return DEVICE_OK;
   }
   
   Button::~Button()
   {
   }
   
   int Button::setSleep(bool doSleep)
   {
       if (doSleep)
       {
           status &= ~DEVICE_BUTTON_STATE;
           status &= ~DEVICE_BUTTON_STATE_HOLD_TRIGGERED;
           clickCount = 0;
           sigma = 0;
       }
       else
       {
           if ( isWakeOnActive())
           {
               if ( buttonActive())
               {
                   sigma = DEVICE_BUTTON_SIGMA_THRESH_LO + 1;
                   status |= DEVICE_BUTTON_STATE;
                   Event evt(id,DEVICE_BUTTON_EVT_DOWN);
                   clickCount = 1;
                   downStartTime = system_timer_current_time();
               }
           }
       }
      
       return DEVICE_OK;
   }
