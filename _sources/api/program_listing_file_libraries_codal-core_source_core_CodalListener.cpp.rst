
.. _program_listing_file_libraries_codal-core_source_core_CodalListener.cpp:

Program Listing for File CodalListener.cpp
==========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_core_CodalListener.cpp>` (``libraries/codal-core/source/core/CodalListener.cpp``)

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
   #include "CodalListener.h"
   
   using namespace codal;
   
   Listener::Listener(uint16_t id, uint16_t value, void (*handler)(Event), uint16_t flags)
   {
       this->id = id;
       this->value = value;
       this->cb = handler;
       this->cb_arg = NULL;
       this->flags = flags;
       this->next = NULL;
       this->evt_queue = NULL;
   }
   
   Listener::Listener(uint16_t id, uint16_t value, void (*handler)(Event, void *), void* arg, uint16_t flags)
   {
       this->id = id;
       this->value = value;
       this->cb_param = handler;
       this->cb_arg = arg;
       this->flags = flags | MESSAGE_BUS_LISTENER_PARAMETERISED;
       this->next = NULL;
       this->evt_queue = NULL;
   }
   
   Listener::~Listener()
   {
       if(this->flags & MESSAGE_BUS_LISTENER_METHOD)
           delete cb_method;
   }
   
   void Listener::queue(Event e)
   {
       int queueDepth;
   
       EventQueueItem *p = evt_queue;
   
       if (evt_queue == NULL)
           evt_queue = new EventQueueItem(e);
       else
       {
           queueDepth = 1;
   
           while (p->next != NULL)
           {
               p = p->next;
               queueDepth++;
           }
   
           if (queueDepth < MESSAGE_BUS_LISTENER_MAX_QUEUE_DEPTH)
               p->next = new EventQueueItem(e);
       }
   }
