
.. _program_listing_file_libraries_codal-core_source_streams_LevelDetector.cpp:

Program Listing for File LevelDetector.cpp
==========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_streams_LevelDetector.cpp>` (``libraries/codal-core/source/streams/LevelDetector.cpp``)

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
   #include "Event.h"
   #include "CodalCompat.h"
   #include "Timer.h"
   #include "LevelDetector.h"
   #include "ErrorNo.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   LevelDetector::LevelDetector(DataSource &source, int highThreshold, int lowThreshold, uint16_t id, bool connectImmediately) : upstream(source)
   {
       this->id = id;
       this->level = 0;
       this->sigma = 0;
       this->windowPosition = 0;
       this->windowSize = LEVEL_DETECTOR_DEFAULT_WINDOW_SIZE;
       this->lowThreshold = lowThreshold;
       this->highThreshold = highThreshold;
       this->status |= LEVEL_DETECTOR_INITIALISED;
       this->activated = false;
       if(connectImmediately){
           upstream.connect(*this);
           activated = true;
       }
   }
   
   int LevelDetector::pullRequest()
   {
       ManagedBuffer b = upstream.pull();
   
       int16_t *data = (int16_t *) &b[0];
   
       int samples = b.length() / 2;
   
       for (int i=0; i < samples; i++)
       {
           if(upstream.getFormat() == DATASTREAM_FORMAT_8BIT_SIGNED){
               sigma += abs((int8_t) *data);
           }
           else
               sigma += abs(*data);
   
           windowPosition++;
   
           if (windowPosition == windowSize)
           {
               level = sigma / windowSize;
   
               sigma = 0;
               windowPosition = 0;
   
               // If 8 bit - then multiply by 8 to upscale result. High 8 bit ~20, High 16 bit ~150 so roughly 8 times higher
               if(upstream.getFormat() == DATASTREAM_FORMAT_8BIT_SIGNED){
                   level = level*8;
               }
   
               if ((!(status & LEVEL_DETECTOR_HIGH_THRESHOLD_PASSED)) && level > highThreshold)
               {
                   Event(id, LEVEL_THRESHOLD_HIGH);
                   status |=  LEVEL_DETECTOR_HIGH_THRESHOLD_PASSED;
                   status &= ~LEVEL_DETECTOR_LOW_THRESHOLD_PASSED;
               }
   
               if ((!(status & LEVEL_DETECTOR_LOW_THRESHOLD_PASSED)) && level < lowThreshold)
               {
                   Event(id, LEVEL_THRESHOLD_LOW);
                   status |=  LEVEL_DETECTOR_LOW_THRESHOLD_PASSED;
                   status &= ~LEVEL_DETECTOR_HIGH_THRESHOLD_PASSED;
               }
           }
   
           data++;
       }
   
       return DEVICE_OK;
   }
   
   /*
    * Determines the instantaneous value of the sensor, in SI units, and returns it.
    *
    * @return The current value of the sensor.
    */
   int LevelDetector::getValue()
   {
       if(!activated){
           // Register with our upstream component: on demand activated
           DMESG("activating LD");
           upstream.connect(*this);
           activated = true;
       }
       return level;
   }
   
   int LevelDetector::setLowThreshold(int value)
   {
       // Protect against churn if the same threshold is set repeatedly.
       if (lowThreshold == value)
           return DEVICE_OK;
   
       // We need to update our threshold
       lowThreshold = value;
   
       // Reset any exisiting threshold state, and enable threshold detection.
       status &= ~LEVEL_DETECTOR_LOW_THRESHOLD_PASSED;
   
       // If a HIGH threshold has been set, ensure it's above the LOW threshold.
       if (highThreshold < lowThreshold)
           setHighThreshold(lowThreshold+1);
   
       return DEVICE_OK;
   }
   
   int LevelDetector::setHighThreshold(int value)
   {
       // Protect against churn if the same threshold is set repeatedly.
       if (highThreshold == value)
           return DEVICE_OK;
   
       // We need to update our threshold
       highThreshold = value;
   
       // Reset any exisiting threshold state, and enable threshold detection.
       status &= ~LEVEL_DETECTOR_HIGH_THRESHOLD_PASSED;
   
       // If a HIGH threshold has been set, ensure it's above the LOW threshold.
       if (lowThreshold > highThreshold)
           setLowThreshold(highThreshold - 1);
   
       return DEVICE_OK;
   }
   
   int LevelDetector::getLowThreshold()
   {
       return lowThreshold;
   }
   
   int LevelDetector::getHighThreshold()
   {
       return highThreshold;
   }
   
   int LevelDetector::setWindowSize(int size)
   {
       if (size <= 0)
           return DEVICE_INVALID_PARAMETER;
   
       this->windowSize = size;
       return DEVICE_OK;
   }
   
   LevelDetector::~LevelDetector()
   {
   }
