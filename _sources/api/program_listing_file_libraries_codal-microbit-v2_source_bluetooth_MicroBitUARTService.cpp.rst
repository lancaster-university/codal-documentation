
.. _program_listing_file_libraries_codal-microbit-v2_source_bluetooth_MicroBitUARTService.cpp:

Program Listing for File MicroBitUARTService.cpp
================================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_bluetooth_MicroBitUARTService.cpp>` (``libraries/codal-microbit-v2/source/bluetooth/MicroBitUARTService.cpp``)

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
   
   #include "ExternalEvents.h"
   #include "MicroBitUARTService.h"
   #include "MicroBitFiber.h"
   #include "ErrorNo.h"
   #include "NotifyEvents.h"
   
   
   const uint8_t  MicroBitUARTService::base_uuid[ 16] =
   { 0x6e, 0x40, 0x00, 0x00, 0xb5, 0xa3, 0xf3, 0x93, 0xe0, 0xa9, 0xe5, 0x0e, 0x24, 0xdc, 0xca, 0x9e };
   
   const uint16_t MicroBitUARTService::serviceUUID               = 0x0001;
   
   // The TX/RX characteristics for the Nordic UART services (NUS) have two common
   // implementations. The codal code is the same, the only difference is how the characterists
   // and their services are advertised.
   //
   // Enable the MICROBIT_BLE_NORDIC_STYLE_UART setting to build microbit projects for applications that
   // connect to generic NUS devices
   // https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/include/bluetooth/services/nus.html
   //
   // Leave the setting undefined (or 0) for standard dal or codal microbit builds
   
   #if CONFIG_ENABLED(MICROBIT_BLE_NORDIC_STYLE_UART)
   const uint16_t MicroBitUARTService::charUUID[ mbbs_cIdxCOUNT] = { 0x0003, 0x0002 };
   #else
   const uint16_t MicroBitUARTService::charUUID[ mbbs_cIdxCOUNT] = { 0x0002, 0x0003 };
   #endif 
   
   #define MICROBIT_UART_S_ATTRSIZE            20
   
   MicroBitUARTService::MicroBitUARTService(BLEDevice &_ble, uint8_t rxBufferSize, uint8_t txBufferSize)
   {
       // Initialise our characteristic values.
       txBufferHead = 0;
       txBufferTail = 0;
       
       rxBufferSize += 1;
       txBufferSize += 1;
   
       // Allocate memory for rxBuffer, rx characteristic, txBuffer, tx characteristic
       int size = rxBufferSize + txBufferSize + 2 * MICROBIT_UART_S_ATTRSIZE;
       rxBuffer = (uint8_t *)malloc(size);
       txBuffer = rxBuffer + rxBufferSize + MICROBIT_UART_S_ATTRSIZE;
       
       memclr( rxBuffer, size);
   
       rxBufferHead = 0;
       rxBufferTail = 0;
       this->rxBufferSize = rxBufferSize;
   
       txBufferHead = 0;
       txBufferTail = 0;
       this->txBufferSize = txBufferSize;
   
       txValueSize  = 0;
   
       waitingForEmpty = false;
   
       // Register the base UUID and create the service.
       RegisterBaseUUID( base_uuid);
       CreateService( serviceUUID);
   
       // Create the data structures that represent each of our characteristics in Soft Device.
       CreateCharacteristic( mbbs_cIdxRX, charUUID[ mbbs_cIdxRX],
                             rxBuffer + rxBufferSize,
                             0, MICROBIT_UART_S_ATTRSIZE,
                             microbit_propWRITE | microbit_propWRITE_WITHOUT);
   
       CreateCharacteristic( mbbs_cIdxTX, charUUID[ mbbs_cIdxTX],
                             txBuffer + txBufferSize,
                             0, MICROBIT_UART_S_ATTRSIZE,
                             microbit_propINDICATE);
   }
   
   
   void MicroBitUARTService::onDisconnect( const microbit_ble_evt_t *p_ble_evt)
   {
       txValueSize = txBufferTail = txBufferHead = 0;
   
       if ( waitingForEmpty)
           MicroBitEvent(MICROBIT_ID_NOTIFY, MICROBIT_UART_S_EVT_TX_EMPTY);
   }
   
   
   void MicroBitUARTService::onConfirmation( const microbit_ble_evt_hvc_t *params)
   {
       if ( params->handle == valueHandle( mbbs_cIdxTX))
       {
           txBufferTail = ( (int)txBufferTail + txValueSize) % txBufferSize;
           txValueSize = 0;
           bool async = !waitingForEmpty;
           MicroBitEvent(MICROBIT_ID_NOTIFY, MICROBIT_UART_S_EVT_TX_EMPTY);
           if ( async)
               sendNext();
       }
   }
   
   
   void MicroBitUARTService::onDataWritten(const microbit_ble_evt_write_t *params)
   {
       if (params->handle == valueHandle( mbbs_cIdxRX))
       {
           uint16_t bytesWritten = params->len;
   
           for(int byteIterator = 0; byteIterator <  bytesWritten; byteIterator++)
           {
               int newHead = (rxBufferHead + 1) % rxBufferSize;
   
               if(newHead != rxBufferTail)
               {
                   char c = params->data[byteIterator];
   
                   int delimeterOffset = 0;
                   int delimLength = this->delimeters.length();
   
                   //iterate through our delimeters (if any) to see if there is a match
                   while(delimeterOffset < delimLength)
                   {
                       //fire an event if there is to block any waiting fibers
                       if(this->delimeters.charAt(delimeterOffset) == c)
                           MicroBitEvent(MICROBIT_ID_BLE_UART, MICROBIT_UART_S_EVT_DELIM_MATCH);
   
                       delimeterOffset++;
                   }
   
                   rxBuffer[rxBufferHead] = c;
   
                   rxBufferHead = newHead;
   
                   if(rxBufferHead == rxBuffHeadMatch)
                   {
                       rxBuffHeadMatch = -1;
                       MicroBitEvent(MICROBIT_ID_BLE_UART, MICROBIT_UART_S_EVT_HEAD_MATCH);
                   }
               }
               else
                   MicroBitEvent(MICROBIT_ID_BLE_UART, MICROBIT_UART_S_EVT_RX_FULL);
           }
       }
   }
   
   void MicroBitUARTService::circularCopy(uint8_t *circularBuff, uint8_t circularBuffSize, uint8_t *linearBuff, uint16_t tailPosition, uint16_t headPosition)
   {
       int toBuffIndex = 0;
   
       while(tailPosition != headPosition)
       {
           linearBuff[toBuffIndex++] = circularBuff[tailPosition];
   
           tailPosition = (tailPosition + 1) % circularBuffSize;
       }
   }
   
   int MicroBitUARTService::getc(MicroBitSerialMode mode)
   {
       if(mode == SYNC_SPINWAIT)
           return MICROBIT_INVALID_PARAMETER;
   
       if(mode == ASYNC)
       {
           if(!isReadable())
               return MICROBIT_NO_DATA;
       }
   
       if(mode == SYNC_SLEEP)
       {
           if(!isReadable())
               eventAfter(1, mode);
       }
   
       char c = rxBuffer[rxBufferTail];
   
       rxBufferTail = (rxBufferTail + 1) % rxBufferSize;
   
       return c;
   }
   
   int MicroBitUARTService::putc(char c, MicroBitSerialMode mode)
   {
       return send( (uint8_t *)&c, 1, mode);
   }
   
   int MicroBitUARTService::send(const uint8_t *buf, int length, MicroBitSerialMode mode)
   {
       if(length < 1 || mode == SYNC_SPINWAIT)
           return MICROBIT_INVALID_PARAMETER;
   
       if( !getConnected() || !indicateChrValueEnabled( mbbs_cIdxTX))
           return MICROBIT_NOT_SUPPORTED;
   
       int bytesWritten = 0;
   
       while ( getConnected() && indicateChrValueEnabled( mbbs_cIdxTX))
       {
           // Add new data that fits in the tx buffer
           while ( bytesWritten < length)
           {
               int nextHead = (txBufferHead + 1) % txBufferSize;
               if( nextHead == txBufferTail)
                   break;
   
               txBuffer[ txBufferHead] = buf[ bytesWritten++];
               txBufferHead = nextHead;
           }
           
           if ( mode == SYNC_SLEEP)
           {
               waitingForEmpty = true;
               fiber_wake_on_event(MICROBIT_ID_NOTIFY, MICROBIT_UART_S_EVT_TX_EMPTY);
               sendNext();
               schedule();
               waitingForEmpty = false;
               if ( bytesWritten == length && txBufferTail == txBufferHead)
                   break;
           }
           else
           {
               sendNext();
               break;
           }
       }
   
       return bytesWritten;
   }
   
   bool MicroBitUARTService::sendNext()
   { 
       if ( txValueSize != 0 || txBufferTail == txBufferHead)
           return false;
   
       if( !getConnected() || !indicateChrValueEnabled( mbbs_cIdxTX))
           return false;
   
       // Duplicate the next tx data into the attribute buffer
       uint8_t *value = txBuffer + txBufferSize;
       int txBufferNext = txBufferTail;
       while ( txValueSize < MICROBIT_UART_S_ATTRSIZE && txBufferNext != txBufferHead)
       {
           value[ txValueSize++] = txBuffer[ txBufferNext];
           txBufferNext = ( txBufferNext + 1) % txBufferSize;
       }
   
       indicateChrValue( mbbs_cIdxTX, value, txValueSize);
       return true;
   }
   
   int MicroBitUARTService::send(ManagedString s, MicroBitSerialMode mode)
   {
       return send((uint8_t *)s.toCharArray(), s.length(), mode);
   }
   
   int MicroBitUARTService::read(uint8_t *buf, int len, MicroBitSerialMode mode)
   {
       if(mode == SYNC_SPINWAIT)
           return MICROBIT_INVALID_PARAMETER;
   
       int i = 0;
   
       if(mode == ASYNC)
       {
           int c;
   
           while(i < len && (c = getc(mode)) >= 0)
           {
               buf[i] = c;
               i++;
           }
       }
   
       if(mode == SYNC_SLEEP)
       {
           if(len > rxBufferedSize())
               eventAfter(len - rxBufferedSize(), mode);
   
           while(i < len)
           {
               buf[i] = (char)getc(mode);
               i++;
           }
       }
   
       return i;
   }
   
   ManagedString MicroBitUARTService::read(int len, MicroBitSerialMode mode)
   {
       uint8_t buf[len + 1];
   
       memclr(&buf, len + 1);
   
       int ret = read(buf, len, mode);
   
       if(ret < 1)
           return ManagedString();
   
       return ManagedString((const char *)buf);
   }
   
   ManagedString MicroBitUARTService::readUntil(ManagedString delimeters, MicroBitSerialMode mode)
   {
       if(mode == SYNC_SPINWAIT)
           return MICROBIT_INVALID_PARAMETER;
   
       int localTail = rxBufferTail;
       int preservedTail = rxBufferTail;
   
       int foundIndex = -1;
   
       //ASYNC mode just iterates through our stored characters checking for any matches.
       while(localTail != rxBufferHead && foundIndex  == -1)
       {
           //we use localTail to prevent modification of the actual tail.
           char c = rxBuffer[localTail];
   
           for(int delimeterIterator = 0; delimeterIterator < delimeters.length(); delimeterIterator++)
               if(delimeters.charAt(delimeterIterator) == c)
                   foundIndex = localTail;
   
           localTail = (localTail + 1) % rxBufferSize;
       }
   
       //if our mode is SYNC_SLEEP, we set up an event to be fired when we see a
       //matching character.
       if(mode == SYNC_SLEEP && foundIndex == -1)
       {
           eventOn(delimeters, mode);
   
           foundIndex = rxBufferHead - 1;
   
           this->delimeters = ManagedString();
       }
   
       if(foundIndex >= 0)
       {
           //calculate our local buffer size
           int localBuffSize = (preservedTail > foundIndex) ? (rxBufferSize - preservedTail) + foundIndex : foundIndex - preservedTail;
   
           uint8_t localBuff[localBuffSize + 1];
   
           memclr(&localBuff, localBuffSize + 1);
   
           circularCopy(rxBuffer, rxBufferSize, localBuff, preservedTail, foundIndex);
   
           //plus one for the character we listened for...
           rxBufferTail = (rxBufferTail + localBuffSize + 1) % rxBufferSize;
   
           return ManagedString((char *)localBuff, localBuffSize);
       }
   
       return ManagedString();
   }
   
   int MicroBitUARTService::eventOn(ManagedString delimeters, MicroBitSerialMode mode)
   {
       if(mode == SYNC_SPINWAIT)
           return MICROBIT_INVALID_PARAMETER;
   
       //configure our head match...
       this->delimeters = delimeters;
   
       //block!
       if(mode == SYNC_SLEEP)
           fiber_wait_for_event(MICROBIT_ID_BLE_UART, MICROBIT_UART_S_EVT_DELIM_MATCH);
   
       return MICROBIT_OK;
   }
   
   int MicroBitUARTService::eventAfter(int len, MicroBitSerialMode mode)
   {
       if(mode == SYNC_SPINWAIT)
           return MICROBIT_INVALID_PARAMETER;
   
       //configure our head match...
       this->rxBuffHeadMatch = (rxBufferHead + len) % rxBufferSize;
   
       //block!
       if(mode == SYNC_SLEEP)
           fiber_wait_for_event(MICROBIT_ID_BLE_UART, MICROBIT_UART_S_EVT_HEAD_MATCH);
   
       return MICROBIT_OK;
   }
   
   int MicroBitUARTService::isReadable()
   {
       return (rxBufferTail != rxBufferHead) ? 1 : 0;
   }
   
   int MicroBitUARTService::rxBufferedSize()
   {
       if(rxBufferTail > rxBufferHead)
           return (rxBufferSize - rxBufferTail) + rxBufferHead;
   
       return rxBufferHead - rxBufferTail;
   }
   
   int MicroBitUARTService::txBufferedSize()
   {
       if(txBufferTail > txBufferHead)
           return (txBufferSize - txBufferTail) + txBufferHead;
   
       return txBufferHead - txBufferTail;
   }
   
   #endif
