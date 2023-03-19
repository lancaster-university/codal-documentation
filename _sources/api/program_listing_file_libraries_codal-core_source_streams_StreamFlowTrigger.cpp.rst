
.. _program_listing_file_libraries_codal-core_source_streams_StreamFlowTrigger.cpp:

Program Listing for File StreamFlowTrigger.cpp
==============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_streams_StreamFlowTrigger.cpp>` (``libraries/codal-core/source/streams/StreamFlowTrigger.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #include "StreamFlowTrigger.h"
   #include "ManagedBuffer.h"
   #include "DataStream.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   StreamFlowTrigger::StreamFlowTrigger( DataSource &source ) : upStream( source )
   {
       this->eventHandler = NULL;
       this->downStream = NULL;
       source.connect( *this );
   }
   
   StreamFlowTrigger::~StreamFlowTrigger()
   {
       // NOP
   }
   
   void StreamFlowTrigger::setDataHandler( void (*handler)(int) )
   {
       this->eventHandler = handler;
   }
   
   ManagedBuffer StreamFlowTrigger::pull()
   {
       (*this->eventHandler)( TRIGGER_PULL );
       return this->upStream.pull();
   }
   
   int StreamFlowTrigger::pullRequest()
   {
       (*this->eventHandler)( TRIGGER_REQUEST );
       if( this->downStream != NULL )
           this->downStream->pullRequest();
       
       return 0;
   }
   
   void StreamFlowTrigger::connect( DataSink &sink )
   {
       this->downStream = &sink;
   }
   
   void StreamFlowTrigger::disconnect()
   {
       this->downStream = NULL;
   }
   
   int StreamFlowTrigger::getFormat()
   {
       return this->upStream.getFormat();
   }
   
   int StreamFlowTrigger::setFormat( int format )
   {
       return this->upStream.setFormat( format );
   }
