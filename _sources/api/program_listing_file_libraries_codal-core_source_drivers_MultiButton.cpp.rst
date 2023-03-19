
.. _program_listing_file_libraries_codal-core_source_drivers_MultiButton.cpp:

Program Listing for File MultiButton.cpp
========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_MultiButton.cpp>` (``libraries/codal-core/source/drivers/MultiButton.cpp``)

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
   #include "MultiButton.h"
   
   using namespace codal;
   
   MultiButton::MultiButton(uint16_t button1, uint16_t button2, uint16_t id)
   {
       this->id = id;
       this->button1 = button1;
       this->button2 = button2;
       this->eventConfiguration = DEVICE_BUTTON_SIMPLE_EVENTS;
   
       if (EventModel::defaultEventBus)
       {
           EventModel::defaultEventBus->listen(button1, DEVICE_EVT_ANY, this, &MultiButton::onButtonEvent,  MESSAGE_BUS_LISTENER_IMMEDIATE);
           EventModel::defaultEventBus->listen(button2, DEVICE_EVT_ANY, this, &MultiButton::onButtonEvent,  MESSAGE_BUS_LISTENER_IMMEDIATE);
       }
   }
   
   uint16_t MultiButton::otherSubButton(uint16_t b)
   {
       return (b == button1 ? button2 : button1);
   }
   
   int MultiButton::isSubButtonPressed(uint16_t button)
   {
       if (button == button1)
           return status & MULTI_BUTTON_STATE_1;
   
       if (button == button2)
           return status & MULTI_BUTTON_STATE_2;
   
       return 0;
   }
   
   int MultiButton::isSubButtonHeld(uint16_t button)
   {
       if (button == button1)
           return status & MULTI_BUTTON_HOLD_TRIGGERED_1;
   
       if (button == button2)
           return status & MULTI_BUTTON_HOLD_TRIGGERED_2;
   
       return 0;
   }
   
   int MultiButton::isSubButtonSupressed(uint16_t button)
   {
       if (button == button1)
           return status & MULTI_BUTTON_SUPRESSED_1;
   
       if (button == button2)
           return status & MULTI_BUTTON_SUPRESSED_2;
   
       return 0;
   }
   
   void MultiButton::setButtonState(uint16_t button, int value)
   {
       if (button == button1)
       {
           if (value)
               status |= MULTI_BUTTON_STATE_1;
           else
               status &= ~MULTI_BUTTON_STATE_1;
       }
   
       if (button == button2)
       {
           if (value)
               status |= MULTI_BUTTON_STATE_2;
           else
               status &= ~MULTI_BUTTON_STATE_2;
       }
   }
   
   void MultiButton::setHoldState(uint16_t button, int value)
   {
       if (button == button1)
       {
           if (value)
               status |= MULTI_BUTTON_HOLD_TRIGGERED_1;
           else
               status &= ~MULTI_BUTTON_HOLD_TRIGGERED_1;
       }
   
       if (button == button2)
       {
           if (value)
               status |= MULTI_BUTTON_HOLD_TRIGGERED_2;
           else
               status &= ~MULTI_BUTTON_HOLD_TRIGGERED_2;
       }
   }
   
   void MultiButton::setSupressedState(uint16_t button, int value)
   {
       if (button == button1)
       {
           if (value)
               status |= MULTI_BUTTON_SUPRESSED_1;
           else
               status &= ~MULTI_BUTTON_SUPRESSED_1;
       }
   
       if (button == button2)
       {
           if (value)
               status |= MULTI_BUTTON_SUPRESSED_2;
           else
               status &= ~MULTI_BUTTON_SUPRESSED_2;
       }
   }
   
   void MultiButton::setEventConfiguration(ButtonEventConfiguration config)
   {
       this->eventConfiguration = config;
   }
   
   void MultiButton::onButtonEvent(Event evt)
   {
       int button = evt.source;
       int otherButton = otherSubButton(button);
   
       switch(evt.value)
       {
           case DEVICE_BUTTON_EVT_DOWN:
               setButtonState(button, 1);
               if(isSubButtonPressed(otherButton))
               {
                   Event e(id, DEVICE_BUTTON_EVT_DOWN);
                   clickCount++;
               }
   
           break;
   
           case DEVICE_BUTTON_EVT_HOLD:
               setHoldState(button, 1);
               if(isSubButtonHeld(otherButton))
                   Event e(id, DEVICE_BUTTON_EVT_HOLD);
   
           break;
   
           case DEVICE_BUTTON_EVT_UP:
               if(isSubButtonPressed(otherButton))
               {
                   Event e(id, DEVICE_BUTTON_EVT_UP);
   
                   if (isSubButtonHeld(button) && isSubButtonHeld(otherButton))
                       Event e(id, DEVICE_BUTTON_EVT_LONG_CLICK);
                   else
                       Event e(id, DEVICE_BUTTON_EVT_CLICK);
   
                   setSupressedState(otherButton, 1);
               }
               else if (!isSubButtonSupressed(button) && eventConfiguration == DEVICE_BUTTON_ALL_EVENTS)
               {
                   if (isSubButtonHeld(button))
                       Event e(button, DEVICE_BUTTON_EVT_LONG_CLICK);
                   else
                       Event e(button, DEVICE_BUTTON_EVT_CLICK);
               }
   
               setButtonState(button, 0);
               setHoldState(button, 0);
               setSupressedState(button, 0);
   
           break;
   
       }
   }
   
   
   int MultiButton::isPressed()
   {
       return ((status & MULTI_BUTTON_STATE_1) && (status & MULTI_BUTTON_STATE_2));
   }
