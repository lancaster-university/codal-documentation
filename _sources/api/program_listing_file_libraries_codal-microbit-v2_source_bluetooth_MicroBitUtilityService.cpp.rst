
.. _program_listing_file_libraries_codal-microbit-v2_source_bluetooth_MicroBitUtilityService.cpp:

Program Listing for File MicroBitUtilityService.cpp
===================================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_bluetooth_MicroBitUtilityService.cpp>` (``libraries/codal-microbit-v2/source/bluetooth/MicroBitUtilityService.cpp``)

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
   
   #include "MicroBitConfig.h"
   
   #if CONFIG_ENABLED(DEVICE_BLE)
   
   #include "MicroBit.h"
   #include "MicroBitUtilityService.h"
   #include "MicroBitUtilityTypes.h"
   
   using namespace codal;
   using namespace MicroBitUtility;
   
   #define MICROBIT_ID_UTILITY_PROCESS 0
   
   #define MicroBitUtilityService_SLEEP 10
   #define MicroBitUtilityService_TIMEOUT 10
   
   namespace MicroBitUtility
   {
       typedef enum replyState_t
       {
           replyStateClear,
           replyStateReady,                // reply has been prepared but not sent
           replyStateError
       } replyState_t;
   };
   
   
   //TODO How to choose service and characteristic IDs?
   const uint16_t MicroBitUtilityService::serviceUUID               = 0x0001;
   const uint16_t MicroBitUtilityService::charUUID[ mbbs_cIdxCOUNT] = { 0x0002 };
   
   
   MicroBitUtilityService *MicroBitUtilityService::shared = NULL;
   
   
   class MicroBitUtilityWorkspace
   {
       public:
   
       request_t request;
       reply_t   reply;
       uint8_t   replyState;
       uint8_t   replyLength;
       uint8_t   jobLow;
       bool      lock;
   
       MicroBitUtilityWorkspace()
       {
           init();
           lock = false;
       }
   
       void init()
       {
           memset( &request, 0, sizeof( request));
           memset( &reply, 0, sizeof( reply));
           replyState = replyStateClear;
           replyLength = 0;
           jobLow = 0;
       }
   
       void setRequest( const void *data, int len)
       {
           init();
           memcpy( &request, data, len);
       }
       
       void setReplyReady( uint32_t replyLen)
       {
           reply.job   = request.job + jobLow;
           replyLength = replyLen;
           replyState  = replyStateReady;
       }
   
       void setReply( uint32_t value)
       {
           memcpy( reply.data, &value, sizeof(uint32_t));
           setReplyReady( sizeof(uint32_t));
       }
       
       void setReplyError( uint32_t error)
       {
           setReply( error);
           replyState = replyStateError;
           reply.job = request.job + jobLowERR;
       }
   
       void onReplySent( const void *data)
       {
           reply_t *reply = (reply_t *) data;
           if ( ( reply->job & 0x0F) != jobLowERR)
           {
               jobLow++;
               if ( jobLow > jobLowMAX)
                   jobLow = 0;
           }
       }
   };
   
   
   MicroBitUtilityService *MicroBitUtilityService::createShared( BLEDevice &_ble, EventModel &_messageBus, MicroBitStorage &_storage, MicroBitLog &_log)
   {
       if ( !shared)
           shared = new MicroBitUtilityService( _ble, _messageBus, _storage, _log);
       return shared;
   }
   
   MicroBitUtilityService::MicroBitUtilityService( BLEDevice &_ble, EventModel &_messageBus, MicroBitStorage &_storage, MicroBitLog &_log) :
       messageBus(_messageBus), storage(_storage), log(_log), workspace(NULL)
   {
       // Initialise data
       memclr( characteristicValue, sizeof( characteristicValue));
   
       // Register the base UUID and create the service.
       RegisterBaseUUID( bs_base_uuid);
       CreateService( serviceUUID);
   
       CreateCharacteristic( mbbs_cIdxCTRL, charUUID[ mbbs_cIdxCTRL],
                            characteristicValue,
                            0, sizeof(characteristicValue),
                            microbit_propWRITE | microbit_propWRITE_WITHOUT | microbit_propNOTIFY);
       
       if ( getConnected())
           listen(true);
   }
   
   
   void MicroBitUtilityService::onConnect( const microbit_ble_evt_t *p_ble_evt)
   {
       listen(true);
   }
   
   
   void MicroBitUtilityService::onDisconnect( const microbit_ble_evt_t *p_ble_evt)
   {
       listen(false);
   }
   
   
   void MicroBitUtilityService::onDataWritten(const microbit_ble_evt_write_t *params)
   {
       if ( params->handle == valueHandle( mbbs_cIdxCTRL) && params->len > 0 && params->len < sizeof(request_t))
       {
           if ( workspace)
           {
               if ( workspace->lock)
                   return;
           }
           else
           {
               workspace = new MicroBitUtilityWorkspace();
               if ( !workspace)
                   return;
           }
           
           workspace->setRequest( params->data, params->len);
           MicroBitEvent evt( MICROBIT_ID_UTILITY, MICROBIT_ID_UTILITY_PROCESS);
       }
   }
   
   
   void MicroBitUtilityService::onEvent(MicroBitEvent e)
   {
       switch (e.source)
       {
           case MICROBIT_ID_UTILITY:
               switch(e.value)
               {
                   case MICROBIT_ID_UTILITY_PROCESS:
                       processRequest();
                       break;
               }
               break;
       }
   }
   
   
   void MicroBitUtilityService::listen( bool yes)
   {
       if ( yes)
           messageBus.listen( MICROBIT_ID_UTILITY, MICROBIT_EVT_ANY, this, &MicroBitUtilityService::onEvent);
       else
           messageBus.ignore( MICROBIT_ID_UTILITY, MICROBIT_EVT_ANY, this, &MicroBitUtilityService::onEvent);
   }
   
   
   int MicroBitUtilityService::sendReply( const void *data, uint16_t length)
   {
       bool ok = notifyChrValue( mbbs_cIdxCTRL, (const uint8_t *) data, length);
       if ( !ok)
           return DEVICE_BUSY;
       workspace->onReplySent( data);
       return DEVICE_OK;
   }
   
   
   int MicroBitUtilityService::processRequest()
   {
       int result = DEVICE_OK;
       
       if ( workspace && !workspace->lock && workspace->request.type != requestTypeNone)
       {
           // Block changes to the request while processing it
           workspace->lock = true;
           
           switch ( workspace->request.type)
           {
               case requestTypeLogLength:
                   result = processLogLength();
                   break;
               case requestTypeLogRead:
                   result = processLogRead();
                   break;
               default:
                   break;
           }
           
           // Check if finished processing the current request
           if ( result == DEVICE_OK)
               workspace->init();
   
           workspace->lock = false;
       }
       
       if ( workspace && workspace->request.type != requestTypeNone)
           MicroBitEvent evt( MICROBIT_ID_UTILITY, MICROBIT_ID_UTILITY_PROCESS);
       return result;
   }
   
   
   int MicroBitUtilityService::processLogLength()
   {
       if ( workspace->replyState == replyStateClear)
       {
           requestLog_t *request = (requestLog_t *) &workspace->request;
           uint32_t length = log.getDataLength( (DataFormat) request->format);
           workspace->setReply( length);
       }
       return sendReply( &workspace->reply, offsetof(reply_t, data) + workspace->replyLength);
   }
   
   
   int MicroBitUtilityService::processLogRead()
   {
       requestLogRead_t *request = (requestLogRead_t *) &workspace->request;
       
       while ( request->batchlen)
       {
           if ( workspace->replyState == replyStateClear)
           {
               int block = min( request->batchlen, sizeof( reply_t) - offsetof( reply_t, data));
               int result = log.readData(workspace->reply.data, request->index, block, (DataFormat) request->format, request->length);
               if ( result)
                   workspace->setReplyError( result);
               else
                   workspace->setReplyReady( block);
           }
           
           int r = sendReply( &workspace->reply, offsetof(reply_t, data) + workspace->replyLength);
           if ( r != DEVICE_OK)
           {
               return r;
           }
           
           if ( workspace->replyState == replyStateError)
           {
               return DEVICE_OK;
           }
           
           workspace->replyState = replyStateClear;
           request->index       += workspace->replyLength;
           request->batchlen    -= workspace->replyLength;
       }
       
       return DEVICE_OK;
   }
   
   #endif
