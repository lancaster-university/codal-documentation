
.. _program_listing_file_libraries_codal-core_source_types_CoordinateSystem.cpp:

Program Listing for File CoordinateSystem.cpp
=============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_types_CoordinateSystem.cpp>` (``libraries/codal-core/source/types/CoordinateSystem.cpp``)

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
   
   #include "CoordinateSystem.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   CoordinateSpace::CoordinateSpace(CoordinateSystem system, bool upsidedown, int rotated)
   {
       this->system = system;
       this->upsidedown = upsidedown;
       this->rotated = rotated;
   }
   
   Sample3D CoordinateSpace::transform(Sample3D s)
   {
       return transform(s, system);
   }
   
   Sample3D CoordinateSpace::transform(Sample3D s, CoordinateSystem system)
   {
       Sample3D result = s;
       int temp;
   
       // If we've been asked to supply raw data, simply return it.
       if (system == RAW)
           return result;
   
       // Firstly, handle any inversions.
       // As we know the input is in ENU format, this means we flip the polarity of the X and Z axes.
       if(upsidedown)
       {
           result.y = -result.y;
           result.z = -result.z;
       }
   
       // Now, handle any rotations.
       switch (rotated)
       {
           case COORDINATE_SPACE_ROTATED_90:
               temp = -result.x;
               result.x = result.y;
               result.y = temp;
               break;
   
           case COORDINATE_SPACE_ROTATED_180:
               result.x = -result.x;
               result.y = -result.y;
               break;
   
           case COORDINATE_SPACE_ROTATED_270:
               temp = result.x;
               result.x = -result.y;
               result.y = temp;
               break;
       }
   
       // Finally, apply coordinate system transformation.
       switch (system)
       {
           case NORTH_EAST_DOWN:
               result.y = -result.y;
               result.z = -result.z;
               break;
   
           case SIMPLE_CARTESIAN:
               temp = result.x;
               result.x = result.y;
               result.y = temp;
               result.z = -result.z;
               break;
   
           default:                    // EAST_NORTH_UP
               break;
       }
   
       return result;
   
   }
   
