
.. _program_listing_file_libraries_codal-core_source_types_Event.cpp:

Program Listing for File Event.cpp
==================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_types_Event.cpp>` (``libraries/codal-core/source/types/Event.cpp``)

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
   #include "Event.h"
   #include "Timer.h"
   #include "EventModel.h"
   
   using namespace codal;
   
   EventModel* EventModel::defaultEventBus = NULL;
   
   REAL_TIME_FUNC
   Event::Event(uint16_t source, uint16_t value, EventLaunchMode mode)
   {
       this->source = source;
       this->value = value;
   
   #if CONFIG_ENABLED(LIGHTWEIGHT_EVENTS)
       this->timestamp = system_timer_current_time();
   #else
       this->timestamp = system_timer_current_time_us();
   #endif
   
       if(mode != CREATE_ONLY)
           this->fire();
   }
   
     REAL_TIME_FUNC
     Event::Event(uint16_t source, uint16_t value, CODAL_TIMESTAMP currentTimeUs, EventLaunchMode mode)
     {
         this->source = source;
         this->value = value;
         this->timestamp = currentTimeUs;
   
         if(mode != CREATE_ONLY)
             this->fire();
     }
   
   
   Event::Event()
   {
       this->source = 0;
       this->value = 0;
   
   #if CONFIG_ENABLED(LIGHTWEIGHT_EVENTS)
       this->timestamp = system_timer_current_time();
   #else
       this->timestamp = system_timer_current_time_us();
   #endif
   }
   
   REAL_TIME_FUNC
   void Event::fire()
   {
       if(EventModel::defaultEventBus)
           EventModel::defaultEventBus->send(*this);
   }
   
   
   EventQueueItem::EventQueueItem(Event evt)
   {
       this->evt = evt;
       this->next = NULL;
   }
