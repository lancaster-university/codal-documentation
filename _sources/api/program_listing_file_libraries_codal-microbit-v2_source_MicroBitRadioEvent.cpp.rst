
.. _program_listing_file_libraries_codal-microbit-v2_source_MicroBitRadioEvent.cpp:

Program Listing for File MicroBitRadioEvent.cpp
===============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_MicroBitRadioEvent.cpp>` (``libraries/codal-microbit-v2/source/MicroBitRadioEvent.cpp``)

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
   
   #include "MicroBitRadio.h"
   
   using namespace codal;
   
   MicroBitRadioEvent::MicroBitRadioEvent(MicroBitRadio &r) : radio(r)
   {
       this->suppressForwarding = false;
   }
   
   int MicroBitRadioEvent::listen(uint16_t id, uint16_t value)
   {
       if (EventModel::defaultEventBus)
           return listen(id, value, *EventModel::defaultEventBus);
   
       return DEVICE_NO_RESOURCES;
   }
   
   int MicroBitRadioEvent::listen(uint16_t id, uint16_t value, EventModel &eventBus)
   {
       return eventBus.listen(id, value, this, &MicroBitRadioEvent::eventReceived, MESSAGE_BUS_LISTENER_IMMEDIATE);
   }
   
   int MicroBitRadioEvent::ignore(uint16_t id, uint16_t value)
   {
       if (EventModel::defaultEventBus)
           return ignore(id, value, *EventModel::defaultEventBus);
   
       return DEVICE_INVALID_PARAMETER;
   }
   
   int MicroBitRadioEvent::ignore(uint16_t id, uint16_t value, EventModel &eventBus)
   {
       return eventBus.ignore(id, value, this, &MicroBitRadioEvent::eventReceived);
   }
   
   
   void MicroBitRadioEvent::packetReceived()
   {
       FrameBuffer *p = radio.recv();
       Event *e = (Event *) p->payload;
   
       suppressForwarding = true;
       e->fire();
       suppressForwarding = false;
   
       delete p;
   }
   
   void MicroBitRadioEvent::eventReceived(Event e)
   {
       if(suppressForwarding)
           return;
   
       FrameBuffer buf;
   
       buf.length = sizeof(Event) + MICROBIT_RADIO_HEADER_SIZE - 1;
       buf.version = 1;
       buf.group = 0;
       buf.protocol = MICROBIT_RADIO_PROTOCOL_EVENTBUS;
       memcpy(buf.payload, (const uint8_t *)&e, sizeof(Event));
   
       radio.send(&buf);
   }
