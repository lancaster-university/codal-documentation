
.. _program_listing_file_libraries_codal-core_source_driver-models_Serial.cpp:

Program Listing for File Serial.cpp
===================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_Serial.cpp>` (``libraries/codal-core/source/driver-models/Serial.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   #include "Serial.h"
   #include "NotifyEvents.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   void Serial::dataReceived(char c)
   {
       if(!(status & CODAL_SERIAL_STATUS_RX_BUFF_INIT))
           return;
   
       int delimeterOffset = 0;
       int delimLength = this->delimeters.length();
   
       //iterate through our delimeters (if any) to see if there is a match
       while(delimeterOffset < delimLength)
       {
           //fire an event if there is to block any waiting fibers
           if(this->delimeters.charAt(delimeterOffset) == c)
               Event(this->id, CODAL_SERIAL_EVT_DELIM_MATCH);
   
           delimeterOffset++;
       }
   
       uint16_t newHead = (rxBuffHead + 1) % rxBuffSize;
   
       //look ahead to our newHead value to see if we are about to collide with the tail
       if(newHead != rxBuffTail)
       {
           //if we are not, store the character, and update our actual head.
           this->rxBuff[rxBuffHead] = c;
           rxBuffHead = newHead;
   
           //if we have any fibers waiting for a specific number of characters, unblock them
           if(rxBuffHeadMatch >= 0)
               if(rxBuffHead == rxBuffHeadMatch)
               {
                   rxBuffHeadMatch = -1;
                   Event(this->id, CODAL_SERIAL_EVT_HEAD_MATCH);
               }
   
           status |= CODAL_SERIAL_STATUS_RXD;
       }
       else
           //otherwise, our buffer is full, send an event to the user...
           Event(this->id, CODAL_SERIAL_EVT_RX_FULL);
   }
   
   void Serial::dataTransmitted()
   {
       if(!(status & CODAL_SERIAL_STATUS_TX_BUFF_INIT))
           return;
   
       //send our current char
       putc((char)txBuff[txBuffTail]);
   
       //unblock any waiting fibers that are waiting for transmission to finish.
       uint16_t nextTail = (txBuffTail + 1) % txBuffSize;
   
       if(nextTail == txBuffHead)
       {
           Event(DEVICE_ID_NOTIFY, CODAL_SERIAL_EVT_TX_EMPTY);
           disableInterrupt(TxInterrupt);
       }
   
       //update our tail!
       txBuffTail = nextTail;
   }
   
   int Serial::setTxInterrupt(uint8_t *string, int len, SerialMode mode)
   {
       int copiedBytes = 0;
   
       while(copiedBytes < len)
       {
           uint16_t nextHead = (txBuffHead + 1) % txBuffSize;
   
           if(nextHead == txBuffTail)
           {
               enableInterrupt(TxInterrupt);
   
               if(mode == SYNC_SLEEP)
                   fiber_wait_for_event(DEVICE_ID_NOTIFY, CODAL_SERIAL_EVT_TX_EMPTY);
   
               if(mode == SYNC_SPINWAIT)
                   while(txBufferedSize() > 0);
   
               if(mode == ASYNC)
                   break;
           }
   
           this->txBuff[txBuffHead] = string[copiedBytes];
           txBuffHead = nextHead;
           copiedBytes++;
       }
   
       //set the TX interrupt
       enableInterrupt(TxInterrupt);
   
       return copiedBytes;
   }
   
   void Serial::idleCallback()
   {
       if (this->status & CODAL_SERIAL_STATUS_RXD)
       {
           Event(this->id, CODAL_SERIAL_EVT_DATA_RECEIVED);
           this->status &= ~CODAL_SERIAL_STATUS_RXD;
       }
   }
   
   void Serial::lockRx()
   {
       status |= CODAL_SERIAL_STATUS_RX_IN_USE;
   }
   
   void Serial::lockTx()
   {
       status |= CODAL_SERIAL_STATUS_TX_IN_USE;
   }
   
   void Serial::unlockRx()
   {
       status &= ~CODAL_SERIAL_STATUS_RX_IN_USE;
   }
   
   void Serial::unlockTx()
   {
       status &= ~CODAL_SERIAL_STATUS_TX_IN_USE;
   }
   
   int Serial::initialiseRx()
   {
       if((status & CODAL_SERIAL_STATUS_RX_BUFF_INIT))
       {
           //ensure that we receive no interrupts after freeing our buffer
           disableInterrupt(RxInterrupt);
           free(this->rxBuff);
       }
   
       status &= ~CODAL_SERIAL_STATUS_RX_BUFF_INIT;
   
       if((this->rxBuff = (uint8_t *)malloc(rxBuffSize)) == NULL)
           return DEVICE_NO_RESOURCES;
   
       this->rxBuffHead = 0;
       this->rxBuffTail = 0;
   
       //set the receive interrupt
       status |= CODAL_SERIAL_STATUS_RX_BUFF_INIT;
       enableInterrupt(RxInterrupt);
   
       return DEVICE_OK;
   }
   
   int Serial::initialiseTx()
   {
       if((status & CODAL_SERIAL_STATUS_TX_BUFF_INIT))
       {
           //ensure that we receive no interrupts after freeing our buffer
           disableInterrupt(TxInterrupt);
           free(this->txBuff);
       }
   
       status &= ~CODAL_SERIAL_STATUS_TX_BUFF_INIT;
   
       if((this->txBuff = (uint8_t *)malloc(txBuffSize)) == NULL)
           return DEVICE_NO_RESOURCES;
   
       this->txBuffHead = 0;
       this->txBuffTail = 0;
   
       status |= CODAL_SERIAL_STATUS_TX_BUFF_INIT;
   
       return DEVICE_OK;
   }
   
   void Serial::circularCopy(uint8_t *circularBuff, uint8_t circularBuffSize, uint8_t *linearBuff, uint16_t tailPosition, uint16_t headPosition)
   {
       int toBuffIndex = 0;
   
       while(tailPosition != headPosition)
       {
           linearBuff[toBuffIndex++] = circularBuff[tailPosition];
   
           tailPosition = (tailPosition + 1) % circularBuffSize;
       }
   }
   
   
   Serial::Serial(Pin& tx, Pin& rx, uint8_t rxBufferSize, uint8_t txBufferSize, uint16_t id) : tx(&tx), rx(&rx)
   {
       this->id = id;
   
       // + 1 so there is a usable buffer size, of the size the user requested.
       this->rxBuffSize = rxBufferSize + 1;
       this->txBuffSize = txBufferSize + 1;
   
       this->rxBuff = NULL;
       this->txBuff = NULL;
   
       this->rxBuffHead = 0;
       this->rxBuffTail = 0;
   
       this->txBuffHead = 0;
       this->txBuffTail = 0;
   
       this->rxBuffHeadMatch = -1;
   
       reassignPin(&this->tx, &tx);
       reassignPin(&this->rx, &rx);
   
       this->status |= DEVICE_COMPONENT_STATUS_IDLE_TICK;
   }
   
   int Serial::sendChar(char c, SerialMode mode)
   {
       return send((uint8_t *)&c, 1, mode);
   }
   
   int Serial::send(ManagedString s, SerialMode mode)
   {
       return send((uint8_t *)s.toCharArray(), s.length(), mode);
   }
   
   int Serial::send(uint8_t *buffer, int bufferLen, SerialMode mode)
   {
       if(txInUse())
           return DEVICE_SERIAL_IN_USE;
   
       if(bufferLen <= 0 || buffer == NULL)
           return DEVICE_INVALID_PARAMETER;
   
       lockTx();
   
       //lazy initialisation of our tx buffer
       if(!(status & CODAL_SERIAL_STATUS_TX_BUFF_INIT))
       {
           int result = initialiseTx();
   
           if(result != DEVICE_OK)
               return result;
       }
   
       int bytesWritten = setTxInterrupt(buffer, bufferLen, mode);
   
       unlockTx();
   
       return bytesWritten;
   }
   
   #if CONFIG_ENABLED(CODAL_PROVIDE_PRINTF)
   void Serial::printf(const char* format, ...)
   {
       va_list arg;
       va_start(arg, format);
   
       const char *end = format;
   
       // We might want to call disable / enable interrupts on the serial line if print is called from ISR context
       char buff[20];
       while (*end)
       {
           char current = *end++;
           if (current == '%')
           {
               uint32_t val = va_arg(arg, uint32_t);
               char* str = (char *)((void *)val);
               char* buffPtr = buff;
               char c = 0;
               bool firstDigitFound = false;
               bool lowerCase = false;
               switch (*end++)
               {
   
               case 'c':
                   putc((char)val);
                   break;
               case 'd':
                   memset(buff, 0, 20);
                   itoa(val, buff);
                   while((c = *buffPtr++) != 0)
                       putc(c);
                   break;
   
               case 's':
                   while((c = *str++) != 0)
                       putc(c);
                   break;
   
               case '%':
                   putc('%');
                   break;
   
               case 'x':
                   lowerCase = true;
                   // fall through
               case 'X':
                   for (uint8_t i = 8; i > 0; i--)
                   {
                       uint8_t digit = ((uint8_t) (val >> ((i - 1) * 4)) & 0x0f) + (uint8_t) '0';
                       if (digit > '9')
                       {
                           if (lowerCase)
                               digit += 39;
                           else
                               digit += 7;
                       }
                       if (digit != '0')
                       {
                           putc((char)digit);
                           firstDigitFound = true;
                       }
                       else if (firstDigitFound || i == 1)
                           putc((char)digit);
                   }
                   break;
               case 'p':
               default:
                   putc('?');
                   putc('?');
                   putc('?');
                   break;
               }
           }
           else
               putc(current);
       }
   
       va_end(arg);
   }
   #endif
   
   int Serial::read(SerialMode mode)
   {
       if(rxInUse())
           return DEVICE_SERIAL_IN_USE;
   
       lockRx();
   
       //lazy initialisation of our buffers
       if(!(status & CODAL_SERIAL_STATUS_RX_BUFF_INIT))
       {
           int result = initialiseRx();
   
           if(result != DEVICE_OK)
               return result;
       }
   
       int c = getChar(mode);
   
       unlockRx();
   
       return c;
   }
   
   int Serial::getChar(SerialMode mode)
   {
       if(mode == ASYNC)
       {
           if(!isReadable())
               return DEVICE_NO_DATA;
       }
   
       if(mode == SYNC_SPINWAIT)
           while(!isReadable());
   
       if(mode == SYNC_SLEEP)
       {
           if(!isReadable())
               eventAfter(1, mode);
       }
   
       char c = rxBuff[rxBuffTail];
   
       rxBuffTail = (rxBuffTail + 1) % rxBuffSize;
   
       return c;
   }
   
   ManagedString Serial::read(int size, SerialMode mode)
   {
       uint8_t buff[size + 1];
   
       memclr(&buff, size + 1);
   
       int returnedSize = read((uint8_t *)buff, size, mode);
   
       if(returnedSize <= 0)
           return ManagedString();
   
       return ManagedString((char *)buff, returnedSize);
   }
   
   int Serial::read(uint8_t *buffer, int bufferLen, SerialMode mode)
   {
       if(rxInUse())
           return DEVICE_SERIAL_IN_USE;
   
       lockRx();
   
       //lazy initialisation of our rx buffer
       if(!(status & CODAL_SERIAL_STATUS_RX_BUFF_INIT))
       {
           int result = initialiseRx();
   
           if(result != DEVICE_OK)
               return result;
       }
   
       int bufferIndex = 0;
   
       int temp = 0;
   
       if(mode == ASYNC)
       {
           while(bufferIndex < bufferLen && (temp = getChar(mode)) != DEVICE_NO_DATA)
           {
               buffer[bufferIndex] = (char)temp;
               bufferIndex++;
           }
       }
   
       if(mode == SYNC_SPINWAIT)
       {
           while(bufferIndex < bufferLen)
           {
               buffer[bufferIndex] = (char)getChar(mode);
               bufferIndex++;
           }
       }
   
       if(mode == SYNC_SLEEP)
       {
           if(bufferLen > rxBufferedSize())
               eventAfter(bufferLen - rxBufferedSize(), mode);
   
           while(bufferIndex < bufferLen)
           {
               buffer[bufferIndex] = (char)getChar(mode);
               bufferIndex++;
           }
       }
   
       unlockRx();
   
       return bufferIndex;
   }
   
   ManagedString Serial::readUntil(ManagedString delimeters, SerialMode mode)
   {
       if(rxInUse())
           return ManagedString();
   
       //lazy initialisation of our rx buffer
       if(!(status & CODAL_SERIAL_STATUS_RX_BUFF_INIT))
       {
           int result = initialiseRx();
   
           if(result != DEVICE_OK)
               return result;
       }
   
       lockRx();
   
       int localTail = rxBuffTail;
       int preservedTail = rxBuffTail;
   
       int foundIndex = -1;
   
       //ASYNC mode just iterates through our stored characters checking for any matches.
       while(localTail != rxBuffHead && foundIndex  == -1)
       {
           //we use localTail to prevent modification of the actual tail.
           char c = rxBuff[localTail];
   
           for(int delimeterIterator = 0; delimeterIterator < delimeters.length(); delimeterIterator++)
               if(delimeters.charAt(delimeterIterator) == c)
                   foundIndex = localTail;
   
           localTail = (localTail + 1) % rxBuffSize;
       }
   
       //if our mode is SYNC_SPINWAIT and we didn't see any matching characters in our buffer
       //spin until we find a match!
       if(mode == SYNC_SPINWAIT)
       {
           while(foundIndex == -1)
           {
               while(localTail == rxBuffHead);
   
               char c = rxBuff[localTail];
   
               for(int delimeterIterator = 0; delimeterIterator < delimeters.length(); delimeterIterator++)
                   if(delimeters.charAt(delimeterIterator) == c)
                       foundIndex = localTail;
   
               localTail = (localTail + 1) % rxBuffSize;
           }
       }
   
       //if our mode is SYNC_SLEEP, we set up an event to be fired when we see a
       //matching character.
       if(mode == SYNC_SLEEP && foundIndex == -1)
       {
           eventOn(delimeters, mode);
   
           foundIndex = rxBuffHead - 1;
           if (foundIndex < 0)
               foundIndex += rxBuffSize;
   
           this->delimeters = ManagedString();
       }
   
       if(foundIndex >= 0)
       {
           //calculate our local buffer size
           int localBuffSize = (preservedTail > foundIndex) ? (rxBuffSize - preservedTail) + foundIndex : foundIndex - preservedTail;
   
           uint8_t localBuff[localBuffSize + 1];
   
           memclr(&localBuff, localBuffSize + 1);
   
           circularCopy(rxBuff, rxBuffSize, localBuff, preservedTail, foundIndex);
   
           //plus one for the character we listened for...
           rxBuffTail = (rxBuffTail + localBuffSize + 1) % rxBuffSize;
   
           unlockRx();
   
           return ManagedString((char *)localBuff, localBuffSize);
       }
   
       unlockRx();
   
       return ManagedString();
   }
   
   int Serial::setBaud(int baudrate)
   {
       if(baudrate < 0)
           return DEVICE_INVALID_PARAMETER;
   
       int ret = setBaudrate((uint32_t)baudrate);
   
       if (ret == DEVICE_OK)
           this->baudrate = baudrate;
   
       return ret;
   }
   
   int Serial::redirect(Pin& tx, Pin& rx)
   {
       if(txInUse() || rxInUse())
           return DEVICE_SERIAL_IN_USE;
   
       lockTx();
       lockRx();
   
       reassignPin(&this->tx, &tx);
       reassignPin(&this->rx, &rx);
   
       if(txBufferedSize() > 0)
           disableInterrupt(TxInterrupt);
   
       disableInterrupt(RxInterrupt);
   
       // To be compatible with V1 behaviour
       rx.setPull( PullMode::Up );
   
       configurePins(tx, rx);
   
       enableInterrupt(RxInterrupt);
   
       if(txBufferedSize() > 0)
           enableInterrupt(TxInterrupt);
   
       this->setBaud(this->baudrate);
   
       unlockRx();
       unlockTx();
   
       return DEVICE_OK;
   }
   
   int Serial::eventAfter(int len, SerialMode mode)
   {
       if(mode == SYNC_SPINWAIT)
           return DEVICE_INVALID_PARAMETER;
   
       // Schedule this fiber to wake on an event from the serial port, if necessary
       if(mode == SYNC_SLEEP)
           fiber_wake_on_event(this->id, CODAL_SERIAL_EVT_HEAD_MATCH);
   
       //configure our head match...
       this->rxBuffHeadMatch = (rxBuffHead + len) % rxBuffSize;
   
       // Deschedule this fiber, if necessary
       if(mode == SYNC_SLEEP)
           schedule();
   
       return DEVICE_OK;
   }
   
   int Serial::eventOn(ManagedString delimeters, SerialMode mode)
   {
       if(mode == SYNC_SPINWAIT)
           return DEVICE_INVALID_PARAMETER;
   
       //configure our head match...
       this->delimeters = delimeters;
   
       //block!
       if(mode == SYNC_SLEEP)
           fiber_wait_for_event(this->id, CODAL_SERIAL_EVT_DELIM_MATCH);
   
       return DEVICE_OK;
   
   }
   
   int Serial::isReadable()
   {
       if(!(status & CODAL_SERIAL_STATUS_RX_BUFF_INIT))
       {
           int result = initialiseRx();
   
           if(result != DEVICE_OK)
               return result;
       }
   
       return (rxBuffTail != rxBuffHead) ? 1 : 0;
   }
   
   int Serial::isWriteable()
   {
       return (txBuffHead != (txBuffTail - 1)) ? 1 : 0;
   }
   
   int Serial::setRxBufferSize(uint8_t size)
   {
       if(rxInUse())
           return DEVICE_SERIAL_IN_USE;
   
       lockRx();
   
       // + 1 so there is a usable buffer size, of the size the user requested.
       if (size != 255)
           size++;
   
       this->rxBuffSize = size;
   
       int result = initialiseRx();
   
       unlockRx();
   
       return result;
   }
   
   int Serial::setTxBufferSize(uint8_t size)
   {
       if(txInUse())
           return DEVICE_SERIAL_IN_USE;
   
       lockTx();
   
       // + 1 so there is a usable buffer size, of the size the user requested.
       if (size != 255)
           size++;
   
       this->txBuffSize = size;
   
       int result = initialiseTx();
   
       unlockTx();
   
       return result;
   }
   
   int Serial::getRxBufferSize()
   {
       return this->rxBuffSize;
   }
   
   int Serial::getTxBufferSize()
   {
       return this->txBuffSize;
   }
   
   int Serial::clearRxBuffer()
   {
       if(rxInUse())
           return DEVICE_SERIAL_IN_USE;
   
       lockRx();
   
       rxBuffTail = rxBuffHead;
   
       unlockRx();
   
       return DEVICE_OK;
   }
   
   int Serial::clearTxBuffer()
   {
       if(txInUse())
           return DEVICE_SERIAL_IN_USE;
   
       lockTx();
   
       txBuffTail = txBuffHead;
   
       unlockTx();
   
       return DEVICE_OK;
   }
   
   int Serial::rxBufferedSize()
   {
       if(rxBuffTail > rxBuffHead)
           return (rxBuffSize - rxBuffTail) + rxBuffHead;
   
       return rxBuffHead - rxBuffTail;
   }
   
   int Serial::txBufferedSize()
   {
       if(txBuffTail > txBuffHead)
           return (txBuffSize - txBuffTail) + txBuffHead;
   
       return txBuffHead - txBuffTail;
   }
   
   int Serial::rxInUse()
   {
       return (status & CODAL_SERIAL_STATUS_RX_IN_USE);
   }
   
   int Serial::txInUse()
   {
       return (status & CODAL_SERIAL_STATUS_TX_IN_USE);
   }
   
   Serial::~Serial()
   {
   
   }
