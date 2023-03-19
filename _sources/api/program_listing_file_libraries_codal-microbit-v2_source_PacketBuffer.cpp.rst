
.. _program_listing_file_libraries_codal-microbit-v2_source_PacketBuffer.cpp:

Program Listing for File PacketBuffer.cpp
=========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_PacketBuffer.cpp>` (``libraries/codal-microbit-v2/source/PacketBuffer.cpp``)

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
   
   #include "PacketBuffer.h"
   #include "ErrorNo.h"
   
   using namespace codal;
   
   // Create the EmptyPacket reference.
   PacketBuffer PacketBuffer::EmptyPacket = PacketBuffer(1);
   
   PacketBuffer::PacketBuffer()
   {
       this->init(NULL, 0, 0);
   }
   
   PacketBuffer::PacketBuffer(int length)
   {
       this->init(NULL, length, 0);
   }
   
   PacketBuffer::PacketBuffer(uint8_t *data, int length, int rssi)
   {
       this->init(data, length, rssi);
   }
   
   PacketBuffer::PacketBuffer(const PacketBuffer &buffer)
   {
       ptr = buffer.ptr;
       ptr->incr();
   }
   
   void PacketBuffer::init(uint8_t *data, int length, int rssi)
   {
       if (length < 0)
           length = 0;
   
       ptr = (PacketData *) malloc(sizeof(PacketData) + length);
       ptr->init();
   
       ptr->length = length;
       ptr->rssi = rssi;
   
       // Copy in the data buffer, if provided.
       if (data)
           memcpy(ptr->payload, data, length);
   }
   
   PacketBuffer::~PacketBuffer()
   {
       ptr->decr();
   }
   
   PacketBuffer& PacketBuffer::operator = (const PacketBuffer &p)
   {
       if(ptr == p.ptr)
           return *this;
   
       ptr->decr();
       ptr = p.ptr;
       ptr->incr();
   
       return *this;
   }
   
   uint8_t PacketBuffer::operator [] (int i) const
   {
       return ptr->payload[i];
   }
   
   uint8_t& PacketBuffer::operator [] (int i)
   {
       return ptr->payload[i];
   }
   
   bool PacketBuffer::operator== (const PacketBuffer& p)
   {
       if (ptr == p.ptr)
           return true;
       else
           return (ptr->length == p.ptr->length && (memcmp(ptr->payload, p.ptr->payload, ptr->length)==0));
   }
   
   int PacketBuffer::setByte(int position, uint8_t value)
   {
       if (position < ptr->length)
       {
           ptr->payload[position] = value;
           return DEVICE_OK;
       }
       else
       {
           return DEVICE_INVALID_PARAMETER;
       }
   }
   
   int PacketBuffer::getByte(int position)
   {
       if (position < ptr->length)
           return ptr->payload[position];
       else
           return DEVICE_INVALID_PARAMETER;
   }
   
   uint8_t*PacketBuffer::getBytes()
   {
       return ptr->payload;
   }
   
   int PacketBuffer::length()
   {
       return ptr->length;
   }
   
   int PacketBuffer::getRSSI()
   {
       return ptr->rssi;
   }
   
   void PacketBuffer::setRSSI(uint8_t rssi)
   {
       ptr->rssi = rssi;
   }
