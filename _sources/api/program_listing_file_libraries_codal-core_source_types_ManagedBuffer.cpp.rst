
.. _program_listing_file_libraries_codal-core_source_types_ManagedBuffer.cpp:

Program Listing for File ManagedBuffer.cpp
==========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_types_ManagedBuffer.cpp>` (``libraries/codal-core/source/types/ManagedBuffer.cpp``)

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
   
   #include "ManagedBuffer.h"
   #include <limits.h>
   #include "CodalCompat.h"
   
   #define REF_TAG REF_TAG_BUFFER
   #define EMPTY_DATA ((BufferData*)(void*)emptyData)
   
   REF_COUNTED_DEF_EMPTY(0, 0)
   
   
   using namespace std;
   using namespace codal;
   
   void ManagedBuffer::initEmpty()
   {
       ptr = EMPTY_DATA;
   }
   
   ManagedBuffer::ManagedBuffer()
   {
       initEmpty();
   }
   
   ManagedBuffer::ManagedBuffer(int length, BufferInitialize initialize)
   {
       this->init(NULL, length, initialize);
   }
   
   ManagedBuffer::ManagedBuffer(uint8_t *data, int length)
   {
       this->init(data, length, BufferInitialize::None);
   }
   
   ManagedBuffer::ManagedBuffer(const ManagedBuffer &buffer)
   {
       ptr = buffer.ptr;
       ptr->incr();
   }
   
   ManagedBuffer::ManagedBuffer(BufferData *p)
   {
       ptr = p;
       ptr->incr();
   }
   
   void ManagedBuffer::init(uint8_t *data, int length, BufferInitialize initialize)
   {
       if (length <= 0) {
           initEmpty();
           return;
       }
   
       ptr = (BufferData *) malloc(sizeof(BufferData) + length);
       REF_COUNTED_INIT(ptr);
   
       ptr->length = length;
   
       // Copy in the data buffer, if provided.
       if (data)
           memcpy(ptr->payload, data, length);
   
       if (initialize == BufferInitialize::Zero)
           memset(ptr->payload, 0, length);
   }
   
   ManagedBuffer::~ManagedBuffer()
   {
       ptr->decr();
   }
   
   ManagedBuffer& ManagedBuffer::operator = (const ManagedBuffer &p)
   {
       if(ptr == p.ptr)
           return *this;
   
       ptr->decr();
       ptr = p.ptr;
       ptr->incr();
   
       return *this;
   }
   
   bool ManagedBuffer::operator== (const ManagedBuffer& p)
   {
       if (ptr == p.ptr)
           return true;
       else
           return (ptr->length == p.ptr->length && (memcmp(ptr->payload, p.ptr->payload, ptr->length)==0));
   }
   
   int ManagedBuffer::setByte(int position, uint8_t value)
   {
       if (0 <= position && (uint16_t)position < ptr->length)
       {
           ptr->payload[position] = value;
           return DEVICE_OK;
       }
       else
       {
           return DEVICE_INVALID_PARAMETER;
       }
   }
   
   int ManagedBuffer::getByte(int position)
   {
       if (0 <= position && (uint16_t)position < ptr->length)
           return ptr->payload[position];
       else
           return DEVICE_INVALID_PARAMETER;
   }
   
   BufferData *ManagedBuffer::leakData()
   {
       BufferData* res = ptr;
       initEmpty();
       return res;
   }
   
   
   int ManagedBuffer::fill(uint8_t value, int offset, int length)
   {
       if (offset < 0 || (uint16_t)offset > ptr->length)
           return DEVICE_INVALID_PARAMETER;
       if (length < 0)
           length = (int)ptr->length;
       length = min(length, (int)ptr->length - offset);
   
       memset(ptr->payload + offset, value, length);
   
       return DEVICE_OK;
   }
   
   ManagedBuffer ManagedBuffer::slice(int offset, int length) const
   {
       offset = min((int)ptr->length, offset);
       if (length < 0)
           length = (int)ptr->length;
       length = min(length, (int)ptr->length - offset);
       return ManagedBuffer(ptr->payload + offset, length);
   }
   
   void ManagedBuffer::shift(int offset, int start, int len)
   {
       if (len < 0) len = (int)ptr->length - start;
       if (start < 0 || start + len > (int)ptr->length || start + len < start
           || len == 0 || offset == 0 || offset == INT_MIN) return;
       if (offset <= -len || offset >= len) {
           fill(0, start, len);
           return;
       }
   
       uint8_t *data = ptr->payload + start;
       if (offset < 0) {
           offset = -offset;
           memmove(data + offset, data, len - offset);
           memset(data, 0, offset);
       } else {
           len = len - offset;
           memmove(data, data + offset, len);
           memset(data + len, 0, offset);
       }
   }
   
   void ManagedBuffer::rotate(int offset, int start, int len)
   {
       if (len < 0) len = (int)ptr->length - start;
       if (start < 0 || start + len > (int)ptr-> length || start + len < start
           || len == 0 || offset == 0 || offset == INT_MIN) return;
   
       if (offset < 0)
           offset += len << 8; // try to make it positive
       offset %= len;
       if (offset < 0)
           offset += len;
   
       uint8_t *data = ptr->payload + start;
   
       uint8_t *n_first = data + offset;
       uint8_t *first = data;
       uint8_t *next = n_first;
       uint8_t *last = data + len;
   
       while (first != next) {
           uint8_t tmp = *first;
           *first++ = *next;
           *next++ = tmp;
           if (next == last) {
               next = n_first;
           } else if (first == n_first) {
               n_first = next;
           }
       }
   }
   
   int ManagedBuffer::writeBuffer(int dstOffset, const ManagedBuffer &src, int srcOffset, int length)
   {
       if (length < 0)
           length = src.length();
   
       if (srcOffset < 0 || dstOffset < 0 || dstOffset > (int)ptr->length)
           return DEVICE_INVALID_PARAMETER;
   
       length = min(src.length() - srcOffset, (int)ptr->length - dstOffset);
   
       if (length < 0)
           return DEVICE_INVALID_PARAMETER;
   
       if (ptr == src.ptr) {
           memmove(getBytes() + dstOffset, src.ptr->payload + srcOffset, length);
       } else {
           memcpy(getBytes() + dstOffset, src.ptr->payload + srcOffset, length);
       }
   
       return DEVICE_OK;
   }
   
   int ManagedBuffer::writeBytes(int offset, uint8_t *src, int length, bool swapBytes)
   {
       if (offset < 0 || length < 0 || offset + length > (int)ptr->length)
           return DEVICE_INVALID_PARAMETER;
   
       if (swapBytes) {
           uint8_t *p = ptr->payload + offset + length;
           for (int i = 0; i < length; ++i)
               *--p = src[i];
       } else {
           memcpy(ptr->payload + offset, src, length);
       }
   
       return DEVICE_OK;
   }
   
   int ManagedBuffer::readBytes(uint8_t *dst, int offset, int length, bool swapBytes) const
   {
       if (offset < 0 || length < 0 || offset + length > (int)ptr->length)
           return DEVICE_INVALID_PARAMETER;
   
       if (swapBytes) {
           uint8_t *p = ptr->payload + offset + length;
           for (int i = 0; i < length; ++i)
               dst[i] = *--p;
       } else {
           memcpy(dst, ptr->payload + offset, length);
       }
   
       return DEVICE_OK;
   }
   
   int ManagedBuffer::truncate(int length)
   {
       if (length < 0 || length > (int)ptr->length)
           return DEVICE_INVALID_PARAMETER;
   
       ptr->length = length;
   
       return DEVICE_OK;
   }
