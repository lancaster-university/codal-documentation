
.. _program_listing_file_libraries_codal-core_source_core_CodalHeapAllocator.cpp:

Program Listing for File CodalHeapAllocator.cpp
===============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_core_CodalHeapAllocator.cpp>` (``libraries/codal-core/source/core/CodalHeapAllocator.cpp``)

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
   
   #include "CodalConfig.h"
   #include "CodalHeapAllocator.h"
   #include "platform_includes.h"
   #include "CodalDevice.h"
   #include "CodalCompat.h"
   #include "CodalDmesg.h"
   #include "ErrorNo.h"
   
   using namespace codal;
   
   #if CONFIG_ENABLED(DEVICE_HEAP_ALLOCATOR)
   
   // A list of all active heap regions, and their dimensions in memory.
   HeapDefinition heap[DEVICE_MAXIMUM_HEAPS] = { };
   uint8_t heap_count = 0;
   
   #if (CODAL_DEBUG >= CODAL_DEBUG_HEAP)
   // Diplays a usage summary about a given heap...
   void device_heap_print(HeapDefinition &heap)
   {
       PROCESSOR_WORD_TYPE blockSize;
       PROCESSOR_WORD_TYPE *block;
       int         totalFreeBlock = 0;
       int         totalUsedBlock = 0;
   
       if (heap.heap_start == NULL)
       {
           DMESG("--- HEAP NOT INITIALISED ---");
           return;
       }
   
       DMESG("heap_start : %p", heap.heap_start);
       DMESG("heap_end   : %p", heap.heap_end);
       DMESG("heap_size  : %d", (int)heap.heap_end - (int)heap.heap_start);
   
       // Disable IRQ temporarily to ensure no race conditions!
       target_disable_irq();
   
       block = heap.heap_start;
       while (block < heap.heap_end)
       {
           blockSize = *block & ~DEVICE_HEAP_BLOCK_FREE;
           if (*block & DEVICE_HEAP_BLOCK_FREE)
               DMESGN("[F:%d] ", blockSize*DEVICE_HEAP_BLOCK_SIZE);
           else
               DMESGN("[U:%d] ", blockSize*DEVICE_HEAP_BLOCK_SIZE);
   
           if (*block & DEVICE_HEAP_BLOCK_FREE)
               totalFreeBlock += blockSize;
           else
               totalUsedBlock += blockSize;
   
           block += blockSize;
       }
   
       // Enable Interrupts
       target_enable_irq();
   
       DMESG("\n");
       DMESG("mb_total_free : %d", totalFreeBlock*DEVICE_HEAP_BLOCK_SIZE);
       DMESG("mb_total_used : %d", totalUsedBlock*DEVICE_HEAP_BLOCK_SIZE);
   }
   
   
   // Diagnostics function. Displays a usage summary about all initialised heaps.
   void device_heap_print()
   {
       for (int i=0; i < heap_count; i++)
       {
           DMESG("\nHEAP %d: ", i);
           device_heap_print(heap[i]);
       }
   }
   #endif
   
   int device_create_heap(PROCESSOR_WORD_TYPE start, PROCESSOR_WORD_TYPE end)
   {
       HeapDefinition *h = &heap[heap_count];
   
   #if CONFIG_ENABLED(CODAL_LOW_LEVEL_VALIDATION)
       // Ensure we don't exceed the maximum number of heap segments.
       if (heap_count == DEVICE_MAXIMUM_HEAPS)
           return DEVICE_NO_RESOURCES;
   
       // Sanity check. Ensure range is valid, large enough and word aligned.
       if (end <= start || end - start < DEVICE_HEAP_BLOCK_SIZE*2 || end % DEVICE_HEAP_BLOCK_SIZE != 0 || start % DEVICE_HEAP_BLOCK_SIZE != 0)
           return DEVICE_INVALID_PARAMETER;
   #endif
   
       // Disable IRQ temporarily to ensure no race conditions!
       target_disable_irq();
   
       // Record the dimensions of this new heap
       h->heap_start = (PROCESSOR_WORD_TYPE *)start;
       h->heap_end = (PROCESSOR_WORD_TYPE *)end;
   
       // Initialise the heap as being completely empty and available for use.
       *h->heap_start = DEVICE_HEAP_BLOCK_FREE | (((PROCESSOR_WORD_TYPE) h->heap_end - (PROCESSOR_WORD_TYPE) h->heap_start) / DEVICE_HEAP_BLOCK_SIZE);
   
       heap_count++;
   
       // Enable Interrupts
       target_enable_irq();
   
   #if (CODAL_DEBUG >= CODAL_DEBUG_HEAP)
       device_heap_print();
   #endif
   
       return DEVICE_OK;
   }
   
   uint32_t device_heap_size(uint8_t heap_index)
   {
       if (heap_index >= heap_count)
           return 0;    
       HeapDefinition *h = &heap[heap_index];
       return (uint8_t*)h->heap_end - (uint8_t*)h->heap_start;
   }
   
   REAL_TIME_FUNC
   void *device_malloc_in(size_t size, HeapDefinition &heap)
   {
       PROCESSOR_WORD_TYPE blockSize = 0;
       PROCESSOR_WORD_TYPE blocksNeeded = size % DEVICE_HEAP_BLOCK_SIZE == 0 ? size / DEVICE_HEAP_BLOCK_SIZE : size / DEVICE_HEAP_BLOCK_SIZE + 1;
       PROCESSOR_WORD_TYPE *block;
       PROCESSOR_WORD_TYPE *next;
   
       if (size <= 0)
           return NULL;
   
       // Account for the index block;
       blocksNeeded++;
   
       // Disable IRQ temporarily to ensure no race conditions!
       target_disable_irq();
   
       // We implement a first fit algorithm with cache to handle rapid churn...
       // We also defragment free blocks as we search, to optimise this and future searches.
       block = heap.heap_start;
       while (block < heap.heap_end)
       {
           // If the block is used, then keep looking.
           if(!(*block & DEVICE_HEAP_BLOCK_FREE))
           {
               block += *block;
               continue;
           }
   
           blockSize = *block & ~DEVICE_HEAP_BLOCK_FREE;
   
           // We have a free block. Let's see if the subsequent ones are too. If so, we can merge...
           next = block + blockSize;
   
           while (*next & DEVICE_HEAP_BLOCK_FREE)
           {
               if (next >= heap.heap_end)
                   break;
   
               // We can merge!
               blockSize += (*next & ~DEVICE_HEAP_BLOCK_FREE);
               *block = blockSize | DEVICE_HEAP_BLOCK_FREE;
   
               next = block + blockSize;
           }
   
           // We have a free block. Let's see if it's big enough.
           // If so, we have a winner.
           if (blockSize >= blocksNeeded)
               break;
   
           // Otherwise, keep looking...
           block += blockSize;
       }
   
       // We're full!
       if (block >= heap.heap_end)
       {
           target_enable_irq();
           return NULL;
       }
   
       // If we're at the end of memory or have very near match then mark the whole segment as in use.
       if (blockSize <= blocksNeeded+1 || block+blocksNeeded+1 >= heap.heap_end)
       {
           // Just mark the whole block as used.
           *block &= ~DEVICE_HEAP_BLOCK_FREE;
       }
       else
       {
           // We need to split the block.
           PROCESSOR_WORD_TYPE *splitBlock = block + blocksNeeded;
           *splitBlock = blockSize - blocksNeeded;
           *splitBlock |= DEVICE_HEAP_BLOCK_FREE;
   
           *block = blocksNeeded;
       }
   
       // Enable Interrupts
       target_enable_irq();
   
       return block+1;
   }
   
   REAL_TIME_FUNC
   void* device_malloc (size_t size)
   {
       static uint8_t initialised = 0;
       void *p;
   
       if (size <= 0)
           return NULL;
   
       if (!initialised)
       {
           heap_count = 0;
   
   #if CONFIG_ENABLED(CODAL_LOW_LEVEL_VALIDATION)
           if(device_create_heap((PROCESSOR_WORD_TYPE)(codal_heap_start), (PROCESSOR_WORD_TYPE)(DEVICE_STACK_BASE) - (PROCESSOR_WORD_TYPE)(DEVICE_STACK_SIZE)) == DEVICE_INVALID_PARAMETER)
               target_panic(DEVICE_HEAP_ERROR);
   #else
           device_create_heap((PROCESSOR_WORD_TYPE)(codal_heap_start), (PROCESSOR_WORD_TYPE)(DEVICE_STACK_BASE) - (PROCESSOR_WORD_TYPE)(DEVICE_STACK_SIZE));
   #endif
           initialised = 1;
       }
   
   #if (DEVICE_MAXIMUM_HEAPS == 1)
       p = device_malloc_in(size, heap[0]);
   #else
       // Assign the memory from the first heap created that has space.
       for (int i=0; i < heap_count; i++)
       {
           p = device_malloc_in(size, heap[i]);
           if (p != NULL)
               break;
       }
   #endif
   
       if (p != NULL)
       {
   #if (CODAL_DEBUG >= CODAL_DEBUG_HEAP)
               DMESG("device_malloc: ALLOCATED: %d [%p]", size, p);
   #endif
               return p;
       }
   
       // We're totally out of options (and memory!).
   #if (CODAL_DEBUG >= CODAL_DEBUG_HEAP)
       // Keep everything transparent if we've not been initialised yet
       DMESG("device_malloc: OUT OF MEMORY [%d]", size);
   #endif
   
   #if CONFIG_ENABLED(DEVICE_PANIC_HEAP_FULL)
       target_panic(DEVICE_OOM);
   #endif
   
       return NULL;
   }
   
   REAL_TIME_FUNC
   void device_free (void *mem)
   {
       PROCESSOR_WORD_TYPE *memory = (PROCESSOR_WORD_TYPE *)mem;
       PROCESSOR_WORD_TYPE *cb = memory-1;
       int i=0;
   
   #if (CODAL_DEBUG >= CODAL_DEBUG_HEAP)
       if (heap_count > 0)
           DMESG("device_free:   %p", mem);
   #endif
       // Sanity check.
       if (memory == NULL)
          return;
   
       // If this memory was created from a heap registered with us, free it.
   
   #if (DEVICE_MAXIMUM_HEAPS > 1)
       for (i=0; i < heap_count; i++)
   #endif
       {
           if(memory > heap[i].heap_start && memory < heap[i].heap_end)
           {
               // The memory block given is part of this heap, so we can simply
               // flag that this memory area is now free, and we're done.
               if (*cb == 0 || *cb & DEVICE_HEAP_BLOCK_FREE)
                   target_panic(DEVICE_HEAP_ERROR);
               *cb |= DEVICE_HEAP_BLOCK_FREE;
               return;
           }
       }
   
       // If we reach here, then the memory is not part of any registered heap.
       target_panic(DEVICE_HEAP_ERROR);
   }
   
   void* calloc (size_t num, size_t size)
   {
       void *mem = malloc(num*size);
   
       if (mem) {
           // without this write, GCC will happily optimize malloc() above into calloc()
           // and remove the memset
           ((uint32_t*)mem)[0] = 1;
           memset(mem, 0, num*size);
       }
   
       return mem;
   }
   
   extern "C" void* device_realloc (void* ptr, size_t size)
   {
       void *mem = malloc(size);
   
       // handle the simplest case - no previous memory allocted.
       if (ptr != NULL && mem != NULL)
       {
   
           // Otherwise we need to copy and free up the old data.
           PROCESSOR_WORD_TYPE *cb = ((PROCESSOR_WORD_TYPE *)ptr) - 1;
           PROCESSOR_WORD_TYPE blockSize = *cb & ~DEVICE_HEAP_BLOCK_FREE;
   
           memcpy(mem, ptr, min(blockSize * sizeof(PROCESSOR_WORD_TYPE), size));
           free(ptr);
       }
   
       return mem;
   }
   
   void *malloc(size_t sz) __attribute__ ((weak, alias ("device_malloc")));
   void free(void *mem) __attribute__ ((weak, alias ("device_free")));
   void* realloc (void* ptr, size_t size) __attribute__ ((weak, alias ("device_realloc")));
   
   
   // make sure the libc allocator is not pulled in
   void *_malloc_r(struct _reent *, size_t len)
   {
       return malloc(len);
   }
   
   void _free_r(struct _reent *, void *addr)
   {
       free(addr);
   }
   
   #endif
