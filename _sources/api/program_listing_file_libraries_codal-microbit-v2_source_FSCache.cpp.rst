
.. _program_listing_file_libraries_codal-microbit-v2_source_FSCache.cpp:

Program Listing for File FSCache.cpp
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_FSCache.cpp>` (``libraries/codal-microbit-v2/source/FSCache.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   Copyright (c) 2021 Lancaster University.
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
   #include "FSCache.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   FSCache::FSCache(NVMController &nvm, int blockSize, int size) : flash(nvm), blockSize(blockSize), cacheSize(size)
   {
       // Initialise space to hold our cached pages.
       cache = (CacheEntry *) malloc(sizeof(CacheEntry)*size);
       memset(cache, 0, sizeof(CacheEntry)*size);
   
       // Reset operation counter (used for least-recently-used cache replacement policy)
       operationCount = 0;
   }
   
   void FSCache::clear()
   {
       for (int i = 0; i < cacheSize; i++)
       {
           if (cache[i].page != NULL)
               free(cache[i].page);
       }
   
       // reset all state.
       memset(cache, 0, sizeof(CacheEntry)*cacheSize);
   
       // Reset operation counter (used for least-recently-used cache replacement policy)
       operationCount = 0;
   
   }
   
   int FSCache::erase(uint32_t address)
   {
       CacheEntry *c = getCacheEntry(address);
   
       // Erase the page in our cache (if it is present)
       if (c != NULL)
       {
           memset(c->page, 0xFF, blockSize);
           c->lastUsed = ++operationCount;
       }
   
       return DEVICE_OK;
   }
   
   int FSCache::read(uint32_t address, const void *data, int len)
   {
       int bytesCopied = 0;
   
       // Ensure that the operation is within the limits of the device
       if (address < flash.getFlashStart() || address + len >= flash.getFlashEnd())
           return DEVICE_INVALID_PARAMETER;
   
       // Read operation may span multiple cache boundaries... so we iterate over blocks as necessary.
       while (bytesCopied < len)
       {
           uint32_t a = address + bytesCopied;
           uint32_t block = (a / blockSize) *blockSize;
           uint32_t offset = a % blockSize;
           uint32_t l = min(len - bytesCopied, blockSize - offset);
           CacheEntry *c = cachePage(block);
   
           memcpy((uint8_t *)data + bytesCopied, c->page + offset, l);
           bytesCopied += l;
       }
   
       return DEVICE_OK;
   }
   
   int FSCache::write(uint32_t address, const void *data, int len)
   {
       int bytesCopied = 0;
   
       // Ensure that the operation is within the limits of the device
       if (address < flash.getFlashStart() || address + len >= flash.getFlashEnd())
           return DEVICE_INVALID_PARAMETER;
   
   #ifdef CODAL_FS_CACHE_VALIDATE
       // Read operation may span multiple cache boundaries... so we iterate over blocks as necessary.
       while (bytesCopied < len)
       {
           uint32_t a = address + bytesCopied;
           uint32_t block = (a / blockSize) *blockSize;
           uint32_t offset = a % blockSize;
           uint32_t l = min(len - bytesCopied, blockSize - offset);
           CacheEntry *c = cachePage(block);
   
           // Validate that a write operation can be performed without needing an erase cycle.
           for (uint32_t i = 0; i < l; i++)
           {
               uint8_t b1 = c->page[offset + i];
               uint8_t b2 = ((uint8_t *)data)[bytesCopied + i];
   
               if ((b1 ^ b2) & b2)
               {
                   DMESG("FS_CACHE: ILLEGAL WRITE OPERAITON ATTEMPTED [ADDRESS: %p] [LENGTH: %d]\n", address, len);
                   return DEVICE_NOT_SUPPORTED;
               }
           }
   
           bytesCopied += l;
       }
   
   #endif
   
       // Write operation is valid. Update cache and perform a write-through operation to FLASH.
       bytesCopied = 0;
       while (bytesCopied < len)
       {
           uint32_t a = address + bytesCopied;
           uint32_t block = (a / blockSize) *blockSize;
           uint32_t offset = a % blockSize;
           uint32_t l = min(len - bytesCopied, blockSize - offset);
           CacheEntry *c = cachePage(block);
   
           uint32_t alignedStart = a & 0xFFFFFFFC;
           uint32_t alignedEnd = (a + l) & 0xFFFFFFFC;
           if ((a + l) & 0x03)
               alignedEnd += 4;
   
           // update cache.
           memcpy(c->page + offset, (uint8_t *)data + bytesCopied, l);
   
           // Write through (maintaining 32-bit aligned operations)
           flash.write(alignedStart, (uint32_t *)(c->page + (alignedStart % blockSize)), (alignedEnd - alignedStart)/4);
   
           // Move to next page
           bytesCopied += l;
       }
   
       return DEVICE_OK;
   }
   
   int FSCache::pin(uint32_t address)
   {
       CacheEntry *c = cachePage(address);
   
       if (c)
       {
           c->flags |= FSCACHE_FLAG_PINNED;
           return DEVICE_OK;
       }
   
       return DEVICE_NOT_SUPPORTED;
   }
   
   int FSCache::unpin(uint32_t address)
   {
       CacheEntry *c = getCacheEntry(address);
   
       if (c)
           c->flags &= ~FSCACHE_FLAG_PINNED;
   
       return DEVICE_OK;
   }
   
   CacheEntry* FSCache::cachePage(uint32_t address)
   {
       CacheEntry *lru = NULL;
   
       // Ensure the page is not already in the cache. If so, then nothing to do...
       lru = getCacheEntry(address);
       if (lru)
           return lru;
   
       // Determine the LRU block to replace, or prefereably unused block.
       lru = &cache[0];
       for (int i = 0; i < cacheSize; i++)
       {
           // Simply return the first empty block we find
           if (cache[i].page == NULL)
           {
               lru = &cache[i];
               break;
           }
   
           // Alternatively, record the least recently used block
           if (!(cache[i].flags & FSCACHE_FLAG_PINNED) && (operationCount - cache[i].lastUsed > operationCount - lru->lastUsed))
               lru = &cache[i];
       }
   
       // We now have the best block to replace. Update metadata and load in the block from storage.
       // We are a write through cache, so all old values are soft state.
       lru->address = address;
       lru->flags = 0;
       lru->lastUsed = ++operationCount;
       if (lru->page == NULL)
           lru->page = (uint8_t *) malloc(blockSize);
   
       flash.read((uint32_t *)lru->page, address, blockSize / 4);
   
       return lru;
   }
   
   CacheEntry *FSCache::getCacheEntry(uint32_t address)
   {
       for (int i = 0; i < cacheSize; i++)
       {
           if (cache[i].address == address && cache[i].page)
           {
               cache[i].lastUsed = ++operationCount;
               return &cache[i];
           }
       }
   
       return NULL;
   }
   
   void FSCache::debug(bool verbose)
   {
       for (int i = 0; i < cacheSize; i++)
           debug(&cache[i], verbose);
   }
   
   void FSCache::debug(CacheEntry *c, bool verbose)
   {
       DMESG("CacheEntry: [address: %p] [lastUsed: %d] [flags: %X]\n", c->address, c->lastUsed, c->flags);
   
       if (verbose)
       {
           int i = 0;
           int lineLength = 32;
           uint8_t *p = (uint8_t *)c->page;
           uint8_t *end = p + blockSize;
   
           while (p < end)
           {
               DMESGN("%x ", *p);
               p++;
               i++;
               if (i == lineLength)
               {
                   DMESGN("\n");
                   i = 0;
               }
           }
   
           DMESGN("\n\n");
       }
   }
