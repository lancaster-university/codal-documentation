
.. _program_listing_file_libraries_codal-core_source_driver-models_Gyroscope.cpp:

Program Listing for File Gyroscope.cpp
======================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_Gyroscope.cpp>` (``libraries/codal-core/source/driver-models/Gyroscope.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   
   Copyright (c) 2017 Lancaster University.
   Copyright (c) 2018 Paul ADAM, Europe.
   
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
   
   #include "Gyroscope.h"
   #include "ErrorNo.h"
   #include "Event.h"
   #include "CodalCompat.h"
   #include "CodalFiber.h"
   
   using namespace codal;
   
   
   Gyroscope::Gyroscope(CoordinateSpace &cspace, uint16_t id) : sample(), sampleENU(), coordinateSpace(cspace)
   {
       // Store our identifiers.
       this->id = id;
       this->status = 0;
   
       // Set a default rate of 50Hz and a +/-2g range.
       this->samplePeriod = 20;
       this->sampleRange = 2;
   }
   
   int Gyroscope::update(Sample3D s)
   {
       // Store the new data, after performing any necessary coordinate transformations.
       sampleENU = s;
       sample = coordinateSpace.transform(s);
   
       // Indicate that pitch and roll data is now stale, and needs to be recalculated if needed.
       status &= ~GYROSCOPE_IMU_DATA_VALID;
   
       // Indicate that a new sample is available
       Event e(id, GYROSCOPE_EVT_DATA_UPDATE);
   
       return DEVICE_OK;
   };
   
   uint32_t Gyroscope::instantaneousAccelerationSquared()
   {
       requestUpdate();
   
       // Use pythagoras theorem to determine the combined force acting on the device.
       return (uint32_t)sample.x*(uint32_t)sample.x + (uint32_t)sample.y*(uint32_t)sample.y + (uint32_t)sample.z*(uint32_t)sample.z;
   }
   
   int Gyroscope::setPeriod(int period)
   {
       int result;
   
       samplePeriod = period;
       result = configure();
   
       samplePeriod = getPeriod();
       return result;
   
   }
   
   int Gyroscope::getPeriod()
   {
       return (int)samplePeriod;
   }
   
   int Gyroscope::setRange(int range)
   {
       int result;
   
       sampleRange = range;
       result = configure();
   
       sampleRange = getRange();
       return result;
   }
   
   int Gyroscope::getRange()
   {
       return (int)sampleRange;
   }
   
   int Gyroscope::configure()
   {
       return DEVICE_NOT_SUPPORTED;
   }
   
   int Gyroscope::requestUpdate()
   {
       return DEVICE_NOT_SUPPORTED;
   }
   
   Sample3D Gyroscope::getSample(CoordinateSystem coordinateSystem)
   {
       requestUpdate();
       return coordinateSpace.transform(sampleENU, coordinateSystem);
   }
   
   Sample3D Gyroscope::getSample()
   {
       requestUpdate();
       return sample;
   }
   
   int Gyroscope::getX()
   {
       requestUpdate();
       return sample.x;
   }
   
   int Gyroscope::getY()
   {
       requestUpdate();
       return sample.y;
   }
   
   int Gyroscope::getZ()
   {
       requestUpdate();
       return sample.z;
   }
   
   Gyroscope::~Gyroscope()
   {
   }
   
