
.. _program_listing_file_libraries_codal-microbit-v2_source_MicroBitRadioDatagram.cpp:

Program Listing for File MicroBitRadioDatagram.cpp
==================================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_MicroBitRadioDatagram.cpp>` (``libraries/codal-microbit-v2/source/MicroBitRadioDatagram.cpp``)

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
   
   MicroBitRadioDatagram::MicroBitRadioDatagram(MicroBitRadio &r) : radio(r)
   {
       this->rxQueue = NULL;
   }
   
   int MicroBitRadioDatagram::recv(uint8_t *buf, int len)
   {
       if (buf == NULL || rxQueue == NULL || len < 0)
           return DEVICE_INVALID_PARAMETER;
   
       // Take the first buffer from the queue.
       FrameBuffer *p = rxQueue;
       rxQueue = rxQueue->next;
   
       int l = min(len, p->length - (MICROBIT_RADIO_HEADER_SIZE - 1));
   
       // Fill in the buffer provided, if possible.
       memcpy(buf, p->payload, l);
   
       delete p;
       return l;
   }
   
   PacketBuffer MicroBitRadioDatagram::recv()
   {
       if (rxQueue == NULL)
           return PacketBuffer::EmptyPacket;
   
       FrameBuffer *p = rxQueue;
       rxQueue = rxQueue->next;
   
       PacketBuffer packet(p->payload, p->length - (MICROBIT_RADIO_HEADER_SIZE - 1), p->rssi);
   
       delete p;
       return packet;
   }
   
   int MicroBitRadioDatagram::send(uint8_t *buffer, int len)
   {
       if (buffer == NULL || len < 0 || len > MICROBIT_RADIO_MAX_PACKET_SIZE + MICROBIT_RADIO_HEADER_SIZE - 1)
           return DEVICE_INVALID_PARAMETER;
   
       FrameBuffer buf;
   
       buf.length = len + MICROBIT_RADIO_HEADER_SIZE - 1;
       buf.version = 1;
       buf.group = 0;
       buf.protocol = MICROBIT_RADIO_PROTOCOL_DATAGRAM;
       memcpy(buf.payload, buffer, len);
   
       return radio.send(&buf);
   }
   
   int MicroBitRadioDatagram::send(PacketBuffer data)
   {
       return send((uint8_t *)data.getBytes(), data.length());
   }
   
   int MicroBitRadioDatagram::send(ManagedString data)
   {
       return send((uint8_t *)data.toCharArray(), data.length());
   }
   
   void MicroBitRadioDatagram::packetReceived()
   {
       FrameBuffer *packet = radio.recv();
       int queueDepth = 0;
   
       // We add to the tail of the queue to preserve causal ordering.
       packet->next = NULL;
   
       if (rxQueue == NULL)
       {
           rxQueue = packet;
       }
       else
       {
           FrameBuffer *p = rxQueue;
           while (p->next != NULL)
           {
               p = p->next;
               queueDepth++;
           }
   
           if (queueDepth >= MICROBIT_RADIO_MAXIMUM_RX_BUFFERS)
           {
               delete packet;
               return;
           }
   
           p->next = packet;
       }
   
       Event(DEVICE_ID_RADIO, MICROBIT_RADIO_EVT_DATAGRAM);
   }
