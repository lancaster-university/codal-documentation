
.. _program_listing_file_libraries_codal-core_source_drivers_LinearAnalogSensor.cpp:

Program Listing for File LinearAnalogSensor.cpp
===============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_LinearAnalogSensor.cpp>` (``libraries/codal-core/source/drivers/LinearAnalogSensor.cpp``)

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
   
   #include "LinearAnalogSensor.h"
   
   using namespace codal;
   
   LinearAnalogSensor::LinearAnalogSensor(Pin &pin, uint16_t id, uint16_t inputFloor, uint16_t inputCeiling, float outputFloor, float outputCeiling) : AnalogSensor(pin, id)
   {
       this->inputFloor = inputFloor;
       this->outputFloor = outputFloor;
       this->conversionFactor = (outputCeiling - outputFloor) / ((float)(inputCeiling - inputFloor));
   }
   
   void LinearAnalogSensor::updateSample()
   {
       float sensorReading;
       float value;
   
       sensorReading = (float) (this->readValue() - this->inputFloor);
   
       value = this->outputFloor + sensorReading * this->conversionFactor;
   
       // If this is the first reading performed, take it a a baseline. Otherwise, perform a decay average to smooth out the data.
       if (!(this->status & ANALOG_SENSOR_INITIALISED))
       {
           this->sensorValue = value;
           this->status |=  ANALOG_SENSOR_INITIALISED;
       }
       else
       {
           this->sensorValue = (this->sensorValue * (1.0f - this->sensitivity)) + (value * this->sensitivity);
       }
   
       checkThresholding();
   }
