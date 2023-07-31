
.. _program_listing_file_libraries_codal-core_source_streams_StreamNormalizer.cpp:

Program Listing for File StreamNormalizer.cpp
=============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_streams_StreamNormalizer.cpp>` (``libraries/codal-core/source/streams/StreamNormalizer.cpp``)

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
   
   #include "StreamNormalizer.h"
   #include "ErrorNo.h"
   
   using namespace codal;
   
   static int read_sample_1(uint8_t *ptr)
   {
       return (int) *ptr;
   }
   
   static int read_sample_2(uint8_t *ptr)
   {
       int8_t *p = (int8_t *) ptr;
       return (int) *p;
   }
   
   static int read_sample_3(uint8_t *ptr)
   {
       uint16_t *p = (uint16_t *) ptr;
       return (int) *p;
   }
   
   static int read_sample_4(uint8_t *ptr)
   {
       int16_t *p = (int16_t *) ptr;
       return (int) *p;
   }
   
   static int read_sample_5(uint8_t *ptr)
   {
       uint32_t *p = (uint32_t *) ptr;
       return (int) (*p >> 8);
   }
   
   static int read_sample_6(uint8_t *ptr)
   {
       int32_t *p = (int32_t *) ptr;
       return (int) (*p >> 8);
   }
   
   static int read_sample_7(uint8_t *ptr)
   {
       uint32_t *p = (uint32_t *) ptr;
       return (int) *p;
   }
   
   static int read_sample_8(uint8_t *ptr)
   {
       int32_t *p = (int32_t *) ptr;
       return (int) *p;
   }
   
   static void write_sample_1(uint8_t *ptr, int value)
   {
       *ptr = (uint8_t) value;
   }
   
   static void write_sample_2(uint8_t *ptr, int value)
   {
       *ptr = (int8_t) value;
   }
   
   static void write_sample_3(uint8_t *ptr, int value)
   {
       *(uint16_t *)ptr = (uint16_t) value;
   }
   
   static void write_sample_4(uint8_t *ptr, int value)
   {
       *(int16_t *)ptr = (int16_t) value;
   }
   
   static void write_sample_5_6(uint8_t *ptr, int value)
   {
       *ptr = value & 0xFF;
       *(ptr+1) = (value>>8) & 0xFF;
       *(ptr+2) = (value>>16) & 0xFF;
   }
   
   static void write_sample_7(uint8_t *ptr, int value)
   {
       *(uint32_t *)ptr = (uint32_t) value;
   }
   
   static void write_sample_8(uint8_t *ptr, int value)
   {
       *(int32_t *)ptr = (int32_t) value;
   }
   
   // Lookup table to optimse parsing of input stream.
   SampleReadFn StreamNormalizer::readSample[] = {read_sample_1, read_sample_1, read_sample_2, read_sample_3, read_sample_4, read_sample_5, read_sample_6, read_sample_7, read_sample_8};
   SampleWriteFn StreamNormalizer::writeSample[] = {write_sample_1, write_sample_1, write_sample_2, write_sample_3, write_sample_4, write_sample_5_6, write_sample_5_6, write_sample_7, write_sample_8};
   
   StreamNormalizer::StreamNormalizer(DataSource &source, float gain, bool normalize, int format, int stabilisation) : upstream(source), output(*this)
   {
       setFormat(format);
       setGain(gain);
       setNormalize(normalize);
       setOrMask(0);
       this->zeroOffsetValid = false;
       this->zeroOffset = 0;
       this->stabilisation = stabilisation;
       this->outputEnabled = normalize && stabilisation ? false : true;
   
       // Register with our upstream component
       source.connect(*this);
   }
   
   ManagedBuffer StreamNormalizer::pull()
   {
       int samples;                // Number of samples in the input buffer.
       int s;                      // The sample being processed, encpasulated inside a 32 bit number.
       uint8_t *data;              // Input buffer read pointer.
       uint8_t *result;            // Output buffer write pointer.
       int inputFormat;            // The format of the input buffer.
       int bytesPerSampleIn;       // number of bit per sample of the input buffer.
       int bytesPerSampleOut;      // number of bit per sample of the input buffer.
       int z = 0;                  // normalized zero point calculated from this buffer.
       int zo = (int) zeroOffset;  // Snapshot of our previously calculate zero point.
       ManagedBuffer buffer;       // The buffer being processed.
       
       // Determine the input format.
       inputFormat = upstream.getFormat();
   
       // If no output format has been selected, infer it from our upstream component.
       if (outputFormat == DATASTREAM_FORMAT_UNKNOWN)
           outputFormat = inputFormat;
   
       // Deterine the sample size of out input and output formats.
       bytesPerSampleIn = DATASTREAM_FORMAT_BYTES_PER_SAMPLE(inputFormat);
       bytesPerSampleOut = DATASTREAM_FORMAT_BYTES_PER_SAMPLE(outputFormat);
   
       // Acquire the buffer to be processed.
       ManagedBuffer inputBuffer = upstream.pull();
       samples = inputBuffer.length() / bytesPerSampleIn;
   
       // Use in place processing where possible, but allocate a new buffer when needed.
       if (DATASTREAM_FORMAT_BYTES_PER_SAMPLE(inputFormat) == DATASTREAM_FORMAT_BYTES_PER_SAMPLE(outputFormat))
           buffer = inputBuffer;
       else
           buffer = ManagedBuffer(samples * bytesPerSampleOut);
       
       // Initialise input an doutput buffer pointers.
       data = &inputBuffer[0];
       result = &buffer[0];
   
       // Iterate over the input samples and apply gain, normalization and output formatting.
       for (int i=0; i < samples; i++)
       {
           // read an input sample, account for the appropriate encoding.
           s = readSample[inputFormat](data);
           data += bytesPerSampleIn;
   
           // Calculate and apply normalization, if configured.
           if (normalize)
           {
               z += s;
               s = s - zo;
           }
   
           // Apply configured gain, and mask if any.
           s = (int) ((float)s * gain);
           s |= orMask;
   
           // Write out the sample.
           writeSample[outputFormat](result, s);
           result += bytesPerSampleOut;
       }
   
       // Store the average sample value as an inferred zero point for the next buffer.
       if (normalize)
       {
           float calculatedZeroOffset = (float)z / (float)samples;
   
           zeroOffset = zeroOffsetValid ? zeroOffset*0.5 + calculatedZeroOffset*0.5 : calculatedZeroOffset;
           zeroOffsetValid = true;
   
           if (stabilisation == 0 || abs((int)zeroOffset - zo) < stabilisation)
               outputEnabled = true;
       }
   
       // Ensure output buffer is the correct size;
       buffer.truncate(samples * bytesPerSampleOut);
   
       return buffer;
   }
   
   int StreamNormalizer::pullRequest()
   {
       return output.pullRequest();
   }
   
   int StreamNormalizer::setNormalize(bool normalize)
   {
       this->normalize = normalize;
       return DEVICE_OK;
   }
   
   bool StreamNormalizer::getNormalize()
   {
       return normalize;
   }
   
   int StreamNormalizer::getFormat()
   {
       if (outputFormat == DATASTREAM_FORMAT_UNKNOWN)
           outputFormat = upstream.getFormat();
   
       return outputFormat;
   }
   
   int StreamNormalizer::setFormat(int format)
   {
       if (format < DATASTREAM_FORMAT_UNKNOWN || format > DATASTREAM_FORMAT_32BIT_SIGNED)
           return DEVICE_INVALID_PARAMETER;
   
       outputFormat = format;
       return DEVICE_OK;
   }
   
   int StreamNormalizer::setGain(float gain)
   {
       this->gain = gain;
       return DEVICE_OK;
   }
   
   float StreamNormalizer::getGain()
   {
       return gain;
   }
   
   int StreamNormalizer::setOrMask(uint32_t mask)
   {
       orMask = mask;
       return DEVICE_OK;
   }
   StreamNormalizer::~StreamNormalizer()
   {
   }
   
   float StreamNormalizer::getSampleRate() {
       return this->upstream.getSampleRate();
   }
   
   float StreamNormalizer::requestSampleRate(float sampleRate) {
       return this->upstream.requestSampleRate( sampleRate );
   }
   
   bool StreamNormalizer::isConnected()
   {
       //return this->output.isConnected();
       return false;
   }
