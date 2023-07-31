
.. _program_listing_file_libraries_codal-core_source_streams_LowPassFilter.cpp:

Program Listing for File LowPassFilter.cpp
==========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_streams_LowPassFilter.cpp>` (``libraries/codal-core/source/streams/LowPassFilter.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #include "LowPassFilter.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   LowPassFilter::LowPassFilter( DataSource &source, float beta, bool deepCopy) : EffectFilter( source, deepCopy )
   {
       this->lpf_value = 1.0;
       setBeta(beta);
   }
   
   LowPassFilter::~LowPassFilter()
   {
   }
   
   void LowPassFilter::applyEffect(ManagedBuffer inputBuffer, ManagedBuffer outputBuffer, int format)
   {
       if( inputBuffer.length() < 1 )
           return;
       
       int bytesPerSample = DATASTREAM_FORMAT_BYTES_PER_SAMPLE(format);
       int sampleCount = inputBuffer.length() / bytesPerSample;
       uint8_t *in = inputBuffer.getBytes();
       uint8_t *out = outputBuffer.getBytes();
   
       for( int i=0; i<sampleCount; i++)
       {
           int value = StreamNormalizer::readSample[format]( in );
           lpf_value = lpf_value - (lpf_beta * (lpf_value - (float)value));
           //lpf_value = value & 0xFE; // Strips the last few bits...
           StreamNormalizer::writeSample[format]( out, (int)lpf_value );
   
           in += bytesPerSample; 
           out += bytesPerSample; 
       }
   }
   
   void LowPassFilter::setBeta( float beta )
   {
       this->lpf_beta = beta;
   }
