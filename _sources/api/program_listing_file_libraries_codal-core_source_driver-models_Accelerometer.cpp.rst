
.. _program_listing_file_libraries_codal-core_source_driver-models_Accelerometer.cpp:

Program Listing for File Accelerometer.cpp
==========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_Accelerometer.cpp>` (``libraries/codal-core/source/driver-models/Accelerometer.cpp``)

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
   
   #include "Accelerometer.h"
   #include "ErrorNo.h"
   #include "Event.h"
   #include "CodalCompat.h"
   #include "CodalFiber.h"
   
   using namespace codal;
   
   
   Accelerometer::Accelerometer(CoordinateSpace &cspace, uint16_t id) : sample(), sampleENU(), coordinateSpace(cspace)
   {
       // Store our identifiers.
       this->id = id;
       this->status = 0;
   
       // Set a default rate of 50Hz and a +/-2g range.
       this->samplePeriod = 20;
       this->sampleRange = 2;
   
       // Initialise gesture history
       this->sigma = 0;
       this->impulseSigma = 0;
       this->lastGesture = ACCELEROMETER_EVT_NONE;
       this->currentGesture = ACCELEROMETER_EVT_NONE;
       this->shake.x = 0;
       this->shake.y = 0;
       this->shake.z = 0;
       this->shake.count = 0;
       this->shake.timer = 0;
       this->shake.impulse_2 = 1;
       this->shake.impulse_3 = 1;
       this->shake.impulse_6 = 1;
       this->shake.impulse_8 = 1;
   }
   
   int Accelerometer::update()
   {
       // Store the new data, after performing any necessary coordinate transformations.
       sample = coordinateSpace.transform(sampleENU);
   
       // Indicate that pitch and roll data is now stale, and needs to be recalculated if needed.
       status &= ~ACCELEROMETER_IMU_DATA_VALID;
   
       // Update gesture tracking
       updateGesture();
   
       // Indicate that a new sample is available
       Event e(id, ACCELEROMETER_EVT_DATA_UPDATE);
   
       return DEVICE_OK;
   };
   
   uint32_t Accelerometer::instantaneousAccelerationSquared()
   {
       // Use pythagoras theorem to determine the combined force acting on the device.
       return (uint32_t)sample.x*(uint32_t)sample.x + (uint32_t)sample.y*(uint32_t)sample.y + (uint32_t)sample.z*(uint32_t)sample.z;
   }
   
   uint16_t Accelerometer::instantaneousPosture()
   {
       bool shakeDetected = false;
   
       // Test for shake events.
       // We detect a shake by measuring zero crossings in each axis. In other words, if we see a strong acceleration to the left followed by
       // a strong acceleration to the right, then we can infer a shake. Similarly, we can do this for each axis (left/right, up/down, in/out).
       //
       // If we see enough zero crossings in succession (ACCELEROMETER_SHAKE_COUNT_THRESHOLD), then we decide that the device
       // has been shaken.
       if ((sample.x < -ACCELEROMETER_SHAKE_TOLERANCE && shake.x) || (sample.x > ACCELEROMETER_SHAKE_TOLERANCE && !shake.x))
       {
           shakeDetected = true;
           shake.x = !shake.x;
       }
   
       if ((sample.y < -ACCELEROMETER_SHAKE_TOLERANCE && shake.y) || (sample.y > ACCELEROMETER_SHAKE_TOLERANCE && !shake.y))
       {
           shakeDetected = true;
           shake.y = !shake.y;
       }
   
       if ((sample.z < -ACCELEROMETER_SHAKE_TOLERANCE && shake.z) || (sample.z > ACCELEROMETER_SHAKE_TOLERANCE && !shake.z))
       {
           shakeDetected = true;
           shake.z = !shake.z;
       }
   
       // If we detected a zero crossing in this sample period, count this.
       if (shakeDetected && shake.count < ACCELEROMETER_SHAKE_COUNT_THRESHOLD)
       {
           shake.count++;
   
           if (shake.count == 1)
               shake.timer = 0;
   
           if (shake.count == ACCELEROMETER_SHAKE_COUNT_THRESHOLD)
           {
               shake.shaken = 1;
               shake.timer = 0;
               return ACCELEROMETER_EVT_SHAKE;
           }
       }
   
       // measure how long we have been detecting a SHAKE event.
       if (shake.count > 0)
       {
           shake.timer++;
   
           // If we've issued a SHAKE event already, and sufficient time has assed, allow another SHAKE event to be issued.
           if (shake.shaken && shake.timer >= ACCELEROMETER_SHAKE_RTX)
           {
               shake.shaken = 0;
               shake.timer = 0;
               shake.count = 0;
           }
   
           // Decay our count of zero crossings over time. We don't want them to accumulate if the user performs slow moving motions.
           else if (!shake.shaken && shake.timer >= ACCELEROMETER_SHAKE_DAMPING)
           {
               shake.timer = 0;
               if (shake.count > 0)
                   shake.count--;
           }
       }
   
       uint32_t force = instantaneousAccelerationSquared();
       if (force < ACCELEROMETER_FREEFALL_THRESHOLD)
           return ACCELEROMETER_EVT_FREEFALL;
   
       // Determine our posture.
       if (sample.x < (-1000 + ACCELEROMETER_TILT_TOLERANCE))
           return ACCELEROMETER_EVT_TILT_LEFT;
   
       if (sample.x > (1000 - ACCELEROMETER_TILT_TOLERANCE))
           return ACCELEROMETER_EVT_TILT_RIGHT;
   
       if (sample.y < (-1000 + ACCELEROMETER_TILT_TOLERANCE))
           return ACCELEROMETER_EVT_TILT_DOWN;
   
       if (sample.y > (1000 - ACCELEROMETER_TILT_TOLERANCE))
           return ACCELEROMETER_EVT_TILT_UP;
   
       if (sample.z < (-1000 + ACCELEROMETER_TILT_TOLERANCE))
           return ACCELEROMETER_EVT_FACE_UP;
   
       if (sample.z > (1000 - ACCELEROMETER_TILT_TOLERANCE))
           return ACCELEROMETER_EVT_FACE_DOWN;
   
       return ACCELEROMETER_EVT_NONE;
   }
   
   void Accelerometer::updateGesture()
   {
       // Check for High/Low G force events - typically impulses, impacts etc.
       // Again, during such spikes, these event take priority of the posture of the device.
       // For these events, we don't perform any low pass filtering.
       uint32_t force = instantaneousAccelerationSquared();
   
       if (force > ACCELEROMETER_2G_THRESHOLD)
       {
           if (force > ACCELEROMETER_2G_THRESHOLD && !shake.impulse_2)
           {
               Event e(DEVICE_ID_GESTURE, ACCELEROMETER_EVT_2G);
               shake.impulse_2 = 1;            
           }
           if (force > ACCELEROMETER_3G_THRESHOLD && !shake.impulse_3)
           {
               Event e(DEVICE_ID_GESTURE, ACCELEROMETER_EVT_3G);
               shake.impulse_3 = 1;
           }
           if (force > ACCELEROMETER_6G_THRESHOLD && !shake.impulse_6)
           {
               Event e(DEVICE_ID_GESTURE, ACCELEROMETER_EVT_6G);
               shake.impulse_6 = 1;
           }
           if (force > ACCELEROMETER_8G_THRESHOLD && !shake.impulse_8)
           {
               Event e(DEVICE_ID_GESTURE, ACCELEROMETER_EVT_8G);
               shake.impulse_8 = 1;
           }
   
           impulseSigma = 0;
       }
   
       // Reset the impulse event onve the acceleration has subsided.
       if (impulseSigma < ACCELEROMETER_GESTURE_DAMPING)
           impulseSigma++;
       else
           shake.impulse_2 = shake.impulse_3 = shake.impulse_6 = shake.impulse_8 = 0;
   
   
       // Determine what it looks like we're doing based on the latest sample...
       uint16_t g = instantaneousPosture();
   
       if (g == ACCELEROMETER_EVT_SHAKE)
       {
           lastGesture = ACCELEROMETER_EVT_SHAKE;
           Event e(DEVICE_ID_GESTURE, ACCELEROMETER_EVT_SHAKE);
           return;
       }
   
       // Perform some low pass filtering to reduce jitter from any detected effects
       if (g == currentGesture)
       {
           if (sigma < ACCELEROMETER_GESTURE_DAMPING)
               sigma++;
       }
       else
       {
           currentGesture = g;
           sigma = 0;
       }
   
       // If we've reached threshold, update our record and raise the relevant event...
       if (currentGesture != lastGesture && sigma >= ACCELEROMETER_GESTURE_DAMPING)
       {
           lastGesture = currentGesture;
           Event e(DEVICE_ID_GESTURE, lastGesture);
       }
   }
   
   int Accelerometer::setPeriod(int period)
   {
       int result;
   
       samplePeriod = period;
       result = configure();
   
       samplePeriod = getPeriod();
       return result;
   
   }
   
   int Accelerometer::getPeriod()
   {
       return (int)samplePeriod;
   }
   
   int Accelerometer::setRange(int range)
   {
       int result;
   
       sampleRange = range;
       result = configure();
   
       sampleRange = getRange();
       return result;
   }
   
   int Accelerometer::getRange()
   {
       return (int)sampleRange;
   }
   
   int Accelerometer::configure()
   {
       return DEVICE_NOT_SUPPORTED;
   }
   
   int Accelerometer::requestUpdate()
   {
       return DEVICE_NOT_SUPPORTED;
   }
   
   Sample3D Accelerometer::getSample(CoordinateSystem coordinateSystem)
   {
       requestUpdate();
       return coordinateSpace.transform(sampleENU, coordinateSystem);
   }
   
   Sample3D Accelerometer::getSample()
   {
       requestUpdate();
       return sample;
   }
   
   int Accelerometer::getX()
   {
       requestUpdate();
       return sample.x;
   }
   
   int Accelerometer::getY()
   {
       requestUpdate();
       return sample.y;
   }
   
   int Accelerometer::getZ()
   {
       requestUpdate();
       return sample.z;
   }
   
   int Accelerometer::getPitch()
   {
       return (int) ((360*getPitchRadians()) / (2*PI));
   }
   
   float Accelerometer::getPitchRadians()
   {
       requestUpdate();
       if (!(status & ACCELEROMETER_IMU_DATA_VALID))
           recalculatePitchRoll();
   
       return pitch;
   }
   
   int Accelerometer::getRoll()
   {
       return (int) ((360*getRollRadians()) / (2*PI));
   }
   
   float Accelerometer::getRollRadians()
   {
       requestUpdate();
       if (!(status & ACCELEROMETER_IMU_DATA_VALID))
           recalculatePitchRoll();
   
       return roll;
   }
   
   void Accelerometer::recalculatePitchRoll()
   {
       double x = (double) sample.x;
       double y = (double) sample.y;
       double z = (double) sample.z;
   
       roll = atan2(x, -z);
       pitch = atan2(y, (x*sin(roll) - z*cos(roll)));
   
       // Handle to the two "negative quadrants", such that we get an output in the +/- 18- degree range.
       // This ensures that the pitch values are consistent with the roll values.
       if (z > 0.0)
       {
           double reference = pitch > 0.0 ? (PI / 2.0) : (-PI / 2.0);
           pitch = reference + (reference - pitch);
       }
   
       status |= ACCELEROMETER_IMU_DATA_VALID;
   }
   
   uint16_t Accelerometer::getGesture()
   {
       return lastGesture;
   }
   
   Accelerometer::~Accelerometer()
   {
   }
   
