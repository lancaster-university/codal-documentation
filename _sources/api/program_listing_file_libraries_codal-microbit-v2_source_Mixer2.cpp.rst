
.. _program_listing_file_libraries_codal-microbit-v2_source_Mixer2.cpp:

Program Listing for File Mixer2.cpp
===================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_Mixer2.cpp>` (``libraries/codal-microbit-v2/source/Mixer2.cpp``)

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
   
   #include "Mixer2.h"
   #include "StreamNormalizer.h"
   #include "ErrorNo.h"
   #include "Timer.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   
   Mixer2::Mixer2(float sampleRate, int sampleRange, int format)
   {
       // Set valid defaults.
       this->channels = NULL;
       this->downStream = NULL;
       this->outputFormat = DATASTREAM_FORMAT_16BIT_UNSIGNED;
       this->bytesPerSampleOut = 2;
       this->volume = 1.0f;
       this->orMask = 0;
       this->silenceLevel = 0.0f;
       this->silent = true;
       this->silenceStartTime = 0;
       this->silenceEndTime = 0;
   
       // Attempt to configure output format to requested value
       this->setFormat(format);
       this->setSampleRate(sampleRate);
       this->setSampleRange(sampleRange);
   }
   
   Mixer2::~Mixer2()
   {
       while (channels)
       {
           MixerChannel *n = channels;
           channels = n->next;
           n->stream->disconnect();
           delete n;
       }
   }
   
   void Mixer2::configureChannel(MixerChannel *c)
   {
       c->volume = 1.0f;
       c->format = c->stream->getFormat();
       c->bytesPerSample = DATASTREAM_FORMAT_BYTES_PER_SAMPLE(c->format);
       c->gain = CONFIG_MIXER_INTERNAL_RANGE / (float) c->range;
       c->skip = c->rate / outputRate;
       c->offset = 0.0f;
   
       if (c->format == DATASTREAM_FORMAT_8BIT_UNSIGNED || c->format == DATASTREAM_FORMAT_16BIT_UNSIGNED)
           c->offset = c->range * -0.5f;       
   }
   
   MixerChannel *Mixer2::addChannel(DataSource &stream, float sampleRate, int sampleRange)
   {
       MixerChannel *c = new MixerChannel();
       c->stream = &stream;
       c->range = sampleRange;
       c->rate = sampleRate ? sampleRate : outputRate;
       c->pullRequests = 0;
       c->in = NULL;
       c->end = NULL;
       c->position = 0;
   
       configureChannel(c);
   
       // Add channel to list.
       c->next = channels;
       channels = c;
       
       // Connect channel to the upstream source.
       stream.connect(*c);
       return c;
   }
   
   int Mixer2::removeChannel( MixerChannel * channel )
   {
       DMESG( "Unsupported operation! Channel retained!" );
       return -1;
   }
   
   ManagedBuffer Mixer2::pull() 
   {
       // Take a local timestamp, in case we need to compute a time when a pice of audio will be played out of the speaker
       CODAL_TIMESTAMP pullTime = system_timer_current_time_us();
   
       // If we have no channels, just return an empty buffer.
       if (!channels)
       {
           downStream->pullRequest();
           return ManagedBuffer(CONFIG_MIXER_BUFFER_SIZE);
       }
   
       // Clear the accumulator buffer
       for (int i=0; i<CONFIG_MIXER_BUFFER_SIZE/bytesPerSampleOut; i++)
           mix[i] = 0.0f;
   
       MixerChannel *next;
       bool silence = true;
   
       for (MixerChannel *ch = channels; ch; ch = next) {
           next = ch->next; // save next in case the current channel gets deleted
   
           // Attempt to discover the stream format if it is not already defined.
           if (ch->format == DATASTREAM_FORMAT_UNKNOWN)
           {
               configureChannel(ch);
   
               // If we still don't know, skip this channel until it decides what it is generating...
               if (ch->format == DATASTREAM_FORMAT_UNKNOWN)      
                   continue;
           }
   
           float *out = &mix[0];
           float *end = &mix[CONFIG_MIXER_BUFFER_SIZE/bytesPerSampleOut];
           int inputFormat = ch->format;
   
           // Check if we need to recalculate skip after a channel rate change
           if( ch->skip == 0.0f )
               ch->skip = ch->rate / outputRate;
   
           while (out < end)
           {
               // precalculate the maximum number of samples the we can process with the current buffer allocations.
               // choose the minimum between the available samples in the input buffer and the space in the output buffer.
               int outLen = (int) (end - out);
               int inLen = ((ch->buffer.length() / ch->bytesPerSample) - ch->position) / ch->skip;
               int len =  min(outLen, inLen);
   
               if (len)
                   silence = false;
   
               uint8_t *d = ch->in;
   
               while(len)
               {
                   d = ch->in + (int)(ch->position * ch->bytesPerSample);
   
                   float v = StreamNormalizer::readSample[inputFormat](d);
                   v += ch->offset;
                   v *= ch->gain;    
                   v *= ch->volume;    
                   *out += v;
    
                   ch->position += ch->skip;
   
                   out++;
                   len--;
               }
   
               // Check if we've completed an input buffer. If so, pull down another if available.
               // if no buffer is available, then move on to the next channel.
               if (inLen < outLen)
               {
                   if (ch->pullRequests == 0)
                       break;
   
                   ch->pullRequests--;
                   ch->buffer = ch->stream->pull();
                   ch->in = &ch->buffer[0];
                   ch->position = 0;
                   ch->end = ch->in + ch->buffer.length();
   
                   if (ch->buffer.length() == 0)
                       break;
               }                
           }
       }       
   
       // If we have silence, set output level to predefined value.
       if (silence && silenceLevel != 0.0f)
       {
           for (int i=0; i<CONFIG_MIXER_BUFFER_SIZE/bytesPerSampleOut; i++)
               mix[i] = silenceLevel;
       }
   
       if (this->silent != silence)
       {
           this->silent = silence;
   
           if (this->silent)
           {
               silenceStartTime = pullTime;
               silenceEndTime = 0;
   
               Event(DEVICE_ID_MIXER, DEVICE_MIXER_EVT_SILENCE);
           }
           else
           {
               silenceEndTime = pullTime;
               Event(DEVICE_ID_MIXER, DEVICE_MIXER_EVT_SOUND);
           }
       }
   
       // Scale and pack to our output format
       ManagedBuffer output = ManagedBuffer(CONFIG_MIXER_BUFFER_SIZE);
       uint8_t *w = &output[0];
       float *r = mix;
   
       int len = output.length() / bytesPerSampleOut;
       float scale = volume * outputRange / CONFIG_MIXER_INTERNAL_RANGE;
       int offset = (outputFormat == DATASTREAM_FORMAT_16BIT_UNSIGNED || outputFormat == DATASTREAM_FORMAT_8BIT_UNSIGNED) ? outputRange/2 : 0;
       float lo = (outputFormat == DATASTREAM_FORMAT_16BIT_UNSIGNED || outputFormat == DATASTREAM_FORMAT_8BIT_UNSIGNED) ? 0 : -outputRange/2;
       float hi = (outputFormat == DATASTREAM_FORMAT_16BIT_UNSIGNED || outputFormat == DATASTREAM_FORMAT_8BIT_UNSIGNED) ? outputRange : outputRange/2;
   
       while(len--)
       {
           float sample = *r * scale;
           sample += offset;
           
           // Clamp output range. Would be nice to use apply some compression here, 
           // but we don't really want ot use more CPU than we already do.
           if (sample < lo)
               sample = lo;
   
           if (sample > hi)
               sample = hi;
   
           // Apply any requested bit mask
           int s = (int)sample;
           s |= orMask;
   
           // Write out the sample.
           StreamNormalizer::writeSample[outputFormat](w, s);
           w += bytesPerSampleOut;
           r++;
       }
   
       // Return the buffer and we're done.
       downStream->pullRequest();
       return output;
   }
   
   int MixerChannel::pullRequest()
   {
       pullRequests++;
       return DEVICE_OK;
   }
   
   void Mixer2::connect(DataSink &sink)
   {
       this->downStream = &sink;
       this->downStream->pullRequest();
   }
   
   bool Mixer2::isConnected()
   {
       return this->downStream != NULL;
   }
   
   int Mixer2::getFormat()
   {
       return outputFormat;
   }
       
   int Mixer2::setFormat(int format)
   {
       if (format == DATASTREAM_FORMAT_16BIT_UNSIGNED || format == DATASTREAM_FORMAT_16BIT_SIGNED || format == DATASTREAM_FORMAT_8BIT_UNSIGNED || format == DATASTREAM_FORMAT_8BIT_SIGNED)
       {
           this->outputFormat = format;
           this->bytesPerSampleOut = DATASTREAM_FORMAT_BYTES_PER_SAMPLE(format);
   
           return DEVICE_OK;
       }
   
       return DEVICE_INVALID_PARAMETER;
   }
   
   int
   Mixer2::setVolume(int volume)
   {
       if (volume < 0 || volume > 1023)
           return DEVICE_INVALID_PARAMETER;
   
       this->volume = (float)volume / 1023.f;
       return DEVICE_OK;
   }
   
   int
   Mixer2::getVolume()
   {
       return (int) (this->volume * 1023.0f);
   }
   
   int Mixer2::setSampleRange(uint16_t sampleRange)
   {
       this->outputRange = (float)sampleRange;
       return DEVICE_OK;
   }
   
   int Mixer2::setSampleRate(float sampleRate)
   {
       this->outputRate = (float)sampleRate;
       
       // Recompute the sub/super sampling constants for each channel.    
       for (MixerChannel *c = channels; c; c=c->next)
           c->skip = c->rate / outputRate;
   
       return DEVICE_OK;
   }
   
   int Mixer2::getSampleRange()
   {
       return (int) this->outputRange;
   }
   
   float Mixer2::getSampleRate()
   {
       return this->outputRate;
   }
   
   int Mixer2::setOrMask(uint32_t mask)
   {
       orMask = mask;
       return DEVICE_OK;
   }
   
   int Mixer2::setSilenceLevel(float level)
   {
       if (level < 0 || level > 1024.0f)
           return DEVICE_INVALID_PARAMETER;
   
       silenceLevel = level - 512.0f;
       return DEVICE_OK;
   }
   
   bool Mixer2::isSilent()
   {
     return silent;
   }
   
   CODAL_TIMESTAMP Mixer2::getSilenceStartTime()
   {
       return silenceStartTime;
   }
   
   CODAL_TIMESTAMP Mixer2::getSilenceEndTime()
   {
       return silenceEndTime;
   }
