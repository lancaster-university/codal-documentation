
.. _program_listing_file_libraries_codal-core_source_types_RefCounted.cpp:

Program Listing for File RefCounted.cpp
=======================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_types_RefCounted.cpp>` (``libraries/codal-core/source/types/RefCounted.cpp``)

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
   #include "CodalDevice.h"
   #include "RefCounted.h"
   
   using namespace codal;
   
   static inline bool isReadOnlyInline(RefCounted *t)
   {
       uint32_t refCount = t->refCount;
   
       if (refCount == 0xffff)
           return true; // object in flash
   
       // Do some sanity checking while we're here
       if (refCount == 1 ||        // object should have been deleted
           (refCount & 1) == 0)    // refCount doesn't look right
           target_panic(DEVICE_HEAP_ERROR);
   
       // Not read only
       return false;
   }
   
   bool RefCounted::isReadOnly()
   {
       return isReadOnlyInline(this);
   }
   
   void RefCounted::incr()
   {
       if (!isReadOnlyInline(this))
         __sync_fetch_and_add(&refCount, 2);
   }
   
   void RefCounted::decr()
   {
       if (isReadOnlyInline(this))
           return;
   
       if (__sync_fetch_and_add(&refCount, -2) == 3 ) {
           destroy();
       }
   }
