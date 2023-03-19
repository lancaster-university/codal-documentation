
.. _program_listing_file_libraries_codal-core_source_streams_DataStream.cpp:

Program Listing for File DataStream.cpp
=======================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_streams_DataStream.cpp>` (``libraries/codal-core/source/streams/DataStream.cpp``)

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
   
   #include "DataStream.h"
   #include "CodalComponent.h"
   #include "CodalFiber.h"
   #include "ErrorNo.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   ManagedBuffer DataSource::pull()
   {
       return ManagedBuffer();
   }
   
   void DataSource::connect(DataSink& )
   {
   }
   
   void DataSource::disconnect()
   {
   }
   
   int DataSource::getFormat()
   {
       return DATASTREAM_FORMAT_UNKNOWN;
   }
   
   int DataSource::setFormat(int format)
   {
       return DEVICE_NOT_SUPPORTED;
   }
   
   float DataSource::getSampleRate() {
       return DATASTREAM_SAMPLE_RATE_UNKNOWN;
   }
   
   float DataSource::requestSampleRate(float sampleRate) {
       // Just consume this by default, we don't _have_ to honour requests for specific rates.
       return DATASTREAM_SAMPLE_RATE_UNKNOWN;
   }
   
   int DataSink::pullRequest()
   {
       return DEVICE_NOT_SUPPORTED;
   }
   
   
   DataStream::DataStream(DataSource &upstream)
   {
       this->bufferCount = 0;
       this->bufferLength = 0;
       this->preferredBufferSize = 0;
       this->pullRequestEventCode = 0;
       this->spaceAvailableEventCode = allocateNotifyEvent();
       this->isBlocking = true;
       this->writers = 0;
   
       this->downStream = NULL;
       this->upStream = &upstream;
   
   }
   
   DataStream::~DataStream()
   {
   }
   
   int DataStream::get(int position)
   {
       for (int i = 0; i < bufferCount; i++)
       {
           if (position < stream[i].length())
               return stream[i].getByte(position);
   
           position = position - stream[i].length();
       }
   
       return DEVICE_INVALID_PARAMETER;
   }
   
   int DataStream::set(int position, uint8_t value)
   {
       for (int i = 0; i < bufferCount; i++)
       {
           if (position < stream[i].length())
           {
               stream[i].setByte(position, value);
               return DEVICE_OK;
           }
   
           position = position - stream[i].length();
       }
   
       return DEVICE_INVALID_PARAMETER;
   }
   
   int DataStream::length()
   {
       return this->bufferLength;
   }
   
   bool DataStream::isReadOnly()
   {
       bool r = true;
   
       for (int i=0; i<bufferCount;i++)
           if (stream[i].isReadOnly() == false)
               r = false;
   
       return r;
   }
   
   void DataStream::connect(DataSink &sink)
   {
       this->downStream = &sink;
       this->upStream->connect(*this);
   }
   
   int DataStream::getFormat()
   {
       return upStream->getFormat();
   }
   
   void DataStream::disconnect()
   {
       this->downStream = NULL;
   }
   
   int DataStream::getPreferredBufferSize()
   {
       return preferredBufferSize;
   }
   
   void DataStream::setPreferredBufferSize(int size)
   {
       this->preferredBufferSize = size;
   }
   
   void DataStream::setBlocking(bool isBlocking)
   {
       this->isBlocking = isBlocking;
   
       // If this is the first time async mode has been used on this stream, allocate the necessary resources.
       if (!isBlocking && this->pullRequestEventCode == 0)
       {
           this->pullRequestEventCode = allocateNotifyEvent();
   
           if(EventModel::defaultEventBus)
               EventModel::defaultEventBus->listen(DEVICE_ID_NOTIFY, pullRequestEventCode, this, &DataStream::onDeferredPullRequest);
       }
   }
   
   ManagedBuffer DataStream::pull()
   {
       ManagedBuffer out = stream[0];
   
       //
       // A simplistic FIFO for now. Copy cost is actually pretty low because ManagedBuffer is a managed type,
       // so we're just moving a few references here.
       //
       if (bufferCount > 0)
       {
           for (int i = 0; i < bufferCount-1; i++)
               stream[i] = stream[i + 1];
   
           stream[bufferCount-1] = ManagedBuffer();
   
           bufferCount--;
           bufferLength = bufferLength - out.length();
       }
   
       Event(DEVICE_ID_NOTIFY_ONE, spaceAvailableEventCode);
   
       return out;
   }
   
   void DataStream::onDeferredPullRequest(Event)
   {
       if (downStream != NULL)
           downStream->pullRequest();
   }
   
   bool DataStream::canPull(int size)
   {
       if(bufferCount + writers >= DATASTREAM_MAXIMUM_BUFFERS)
           return false;
   
       if(preferredBufferSize > 0 && (bufferLength + size > preferredBufferSize))
           return false;
   
       return true;
   }
   
   bool DataStream::full()
   {
       return !canPull();
   }
   
   int DataStream::pullRequest()
   {
       // If we're defined as non-blocking and no space is available, then there's nothing we can do.
       if (full() && this->isBlocking == false)
           return DEVICE_NO_RESOURCES;
   
       // As there is either space available in the buffer or we want to block, pull the upstream buffer to release resources there.
       ManagedBuffer buffer = upStream->pull();
   
       // If pull is called multiple times in a row (yielding nothing after the first time)
       // several streams might be woken up, despite the fact that there is no space for them.
       do {
           // If the buffer is full or we're behind another fiber, then wait for space to become available.
           if (full() || writers)
               fiber_wake_on_event(DEVICE_ID_NOTIFY, spaceAvailableEventCode);
   
           if (full() || writers)
           {
               writers++;
               schedule();
               writers--;
           }
       } while (bufferCount >= DATASTREAM_MAXIMUM_BUFFERS);
   
       stream[bufferCount] = buffer;
       bufferLength = bufferLength + buffer.length();
       bufferCount++;
   
       if (downStream != NULL)
       {
           if (this->isBlocking)
               downStream->pullRequest();
           else
               Event(DEVICE_ID_NOTIFY, pullRequestEventCode);
           
       }
   
       return DEVICE_OK;
   }
   
   float DataStream::getSampleRate() {
       if( this->upStream != NULL )
           return this->upStream->getSampleRate();
       return DATASTREAM_SAMPLE_RATE_UNKNOWN;
   }
   
   float DataStream::requestSampleRate(float sampleRate) {
       if( this->upStream != NULL )
           return this->upStream->requestSampleRate( sampleRate );
       return DATASTREAM_SAMPLE_RATE_UNKNOWN;
   }
