
.. _program_listing_file_libraries_codal-core_source_streams_EffectFilter.cpp:

Program Listing for File EffectFilter.cpp
=========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_streams_EffectFilter.cpp>` (``libraries/codal-core/source/streams/EffectFilter.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #include "EffectFilter.h"
   #include "ManagedBuffer.h"
   #include "DataStream.h"
   #include "StreamNormalizer.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   EffectFilter::EffectFilter(DataSource &source, bool deepCopy) : upStream( source )
   {
       this->downStream = NULL;
       this->deepCopy = deepCopy;
       source.connect( *this );
   }
   
   EffectFilter::~EffectFilter()
   {
   }
   
   ManagedBuffer EffectFilter::pull()
   {
       ManagedBuffer input = this->upStream.pull();
       ManagedBuffer output = deepCopy ? ManagedBuffer(input.length()) : input;
   
       applyEffect(input, output, this->upStream.getFormat());
       return output;
   }
   
   int EffectFilter::pullRequest()
   {
       if( this->downStream != NULL )
           this->downStream->pullRequest();
   
       return 0;
   }
   
   void EffectFilter::connect(DataSink &sink)
   {
       this->downStream = &sink;
   }
   
   void EffectFilter::disconnect()
   {
       this->downStream = NULL;
   }
   
   int EffectFilter::getFormat()
   {
       return this->upStream.getFormat();
   }
   
   int EffectFilter::setFormat( int format )
   {
       return this->upStream.setFormat( format );
   }
   
   float EffectFilter::getSampleRate()
   {
       return this->upStream.getSampleRate();
   }
   
   float EffectFilter::requestSampleRate(float sampleRate)
   {
       return this->upStream.requestSampleRate( sampleRate );
   }
   
   void EffectFilter::setDeepCopy( bool deepCopy )
   {
       this->deepCopy = deepCopy;
   }
   
   void EffectFilter::applyEffect(ManagedBuffer inputBuffer, ManagedBuffer outputBuffer, int format)
   {
       if (inputBuffer.getBytes() != outputBuffer.getBytes())
           memcpy(outputBuffer.getBytes(), inputBuffer.getBytes(), inputBuffer.length());
   }
