
.. _program_listing_file_libraries_codal-core_source_driver-models_Compass.cpp:

Program Listing for File Compass.cpp
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_driver-models_Compass.cpp>` (``libraries/codal-core/source/driver-models/Compass.cpp``)

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
   
   #include "Compass.h"
   #include "ErrorNo.h"
   #include "Event.h"
   #include "CodalCompat.h"
   #include "CodalFiber.h"
   
   #define CALIBRATED_SAMPLE(sample, axis) (((sample.axis - calibration.centre.axis) * calibration.scale.axis) >> 10)
   
   using namespace codal;
   
   Compass::Compass(CoordinateSpace &cspace, uint16_t id) : sample(), sampleENU(), coordinateSpace(cspace)
   {
       accelerometer = NULL;
       init(id);
   }
   
   Compass::Compass(Accelerometer &accel, CoordinateSpace &cspace, uint16_t id) :  sample(), sampleENU(), coordinateSpace(cspace)
   {
       accelerometer = &accel;
       init(id);
   }
   
   void Compass::init(uint16_t id)
   {
       // Store our identifiers.
       this->id = id;
       this->status = 0;
   
       // Set a default rate of 50Hz.
       this->samplePeriod = 20;
       this->configure();
   
       // Assume that we have no calibration information.
       status &= ~COMPASS_STATUS_CALIBRATED;
   
       // Indicate that we're up and running.
       status |= DEVICE_COMPONENT_RUNNING;
   }
   
   
   int Compass::heading()
   {
       if(status & COMPASS_STATUS_CALIBRATING)
           return DEVICE_CALIBRATION_IN_PROGRESS;
   
       if(!(status & COMPASS_STATUS_CALIBRATED))
           calibrate();
   
       if(accelerometer != NULL)
           return tiltCompensatedBearing();
   
       return basicBearing();
   }
   
   int Compass::getFieldStrength()
   {
       Sample3D s = getSample();
   
       double x = s.x;
       double y = s.y;
       double z = s.z;
   
       return (int) sqrt(x*x + y*y + z*z);
   }
   
   int Compass::calibrate()
   {
       // Only perform one calibration process at a time.
       if(isCalibrating())
           return DEVICE_CALIBRATION_IN_PROGRESS;
   
       requestUpdate();
   
       // Delete old calibration data
       clearCalibration();
   
       // Record that we've started calibrating.
       status |= COMPASS_STATUS_CALIBRATING;
   
       // Launch any registred calibration alogrithm visialisation
       Event(id, COMPASS_EVT_CALIBRATE);
   
       // Record that we've finished calibrating.
       status &= ~COMPASS_STATUS_CALIBRATING;
   
       // If there are no changes to our sample data, we either have no calibration algorithm, or it couldn't complete succesfully.
       if(!(status & COMPASS_STATUS_CALIBRATED))
           return DEVICE_CALIBRATION_REQUIRED;
   
       return DEVICE_OK;
   }
   
   void Compass::setCalibration(CompassCalibration calibration)
   {
       this->calibration = calibration;
       status |= COMPASS_STATUS_CALIBRATED;
   }
   
   CompassCalibration Compass::getCalibration()
   {
       return calibration;
   }
   
   int Compass::isCalibrated()
   {
       return status & COMPASS_STATUS_CALIBRATED;
   }
   
   int Compass::isCalibrating()
   {
       return status & COMPASS_STATUS_CALIBRATING;
   }
   
   void Compass::clearCalibration()
   {
       calibration = CompassCalibration();
       status &= ~COMPASS_STATUS_CALIBRATED;
   }
   
   void Compass::setAccelerometer(Accelerometer &accelerometer)
   {
       this->accelerometer = &accelerometer;
   }
   
   int Compass::configure()
   {
       return DEVICE_NOT_SUPPORTED;
   }
   
   int Compass::setPeriod(int period)
   {
       int result;
   
       samplePeriod = period;
       result = configure();
   
       samplePeriod = getPeriod();
       return result;
   
   }
   
   int Compass::getPeriod()
   {
       return (int)samplePeriod;
   }
   
   int Compass::requestUpdate()
   {
       return DEVICE_NOT_SUPPORTED;
   }
   
   int Compass::update()
   {
       // Store the raw data, and apply any calibration data we have.
       sampleENU.x = CALIBRATED_SAMPLE(sampleENU, x);
       sampleENU.y = CALIBRATED_SAMPLE(sampleENU, y);
       sampleENU.z = CALIBRATED_SAMPLE(sampleENU, z);
   
       // Store the user accessible data, in the requested coordinate space, and taking into account component placement of the sensor.
       sample = coordinateSpace.transform(sampleENU);
   
       // Indicate that a new sample is available
       Event e(id, COMPASS_EVT_DATA_UPDATE);
   
       return DEVICE_OK;
   };
   
   Sample3D Compass::getSample(CoordinateSystem coordinateSystem)
   {
       requestUpdate();
       return coordinateSpace.transform(sampleENU, coordinateSystem);
   }
   
   Sample3D Compass::getSample()
   {
       requestUpdate();
       return sample;
   }
   
   int Compass::getX()
   {
       requestUpdate();
       return sample.x;
   }
   
   int Compass::getY()
   {
       requestUpdate();
       return sample.y;
   }
   
   int Compass::getZ()
   {
       requestUpdate();
       return sample.z;
   }
   
   int Compass::tiltCompensatedBearing()
   {
       // Precompute the tilt compensation parameters to improve readability.
       float phi = accelerometer->getRollRadians();
       float theta = accelerometer->getPitchRadians();
   
       Sample3D s = getSample(NORTH_EAST_DOWN);
   
       float x = (float) s.x;
       float y = (float) s.y;
       float z = (float) s.z;
   
       // Precompute cos and sin of pitch and roll angles to make the calculation a little more efficient.
       float sinPhi = sin(phi);
       float cosPhi = cos(phi);
       float sinTheta = sin(theta);
       float cosTheta = cos(theta);
   
        // Calculate the tilt compensated bearing, and convert to degrees.
       float bearing = (360*atan2(x*cosTheta + y*sinTheta*sinPhi + z*sinTheta*cosPhi, z*sinPhi - y*cosPhi)) / (2*PI);
   
       // Handle the 90 degree offset caused by the NORTH_EAST_DOWN based calculation.
       bearing = 90 - bearing;
   
       // Ensure the calculated bearing is in the 0..359 degree range.
       if (bearing < 0)
           bearing += 360.0f;
   
       return (int) (bearing);
   }
   
   int Compass::basicBearing()
   {
       // Convert to floating point to reduce rounding errors
       Sample3D cs = this->getSample(SIMPLE_CARTESIAN);
       float x = (float) cs.x;
       float y = (float) cs.y;
   
       float bearing = (atan2(x,y))*180/PI;
   
       if (bearing < 0)
           bearing += 360.0;
   
       return (int)bearing;
   }
   
   Compass::~Compass()
   {
   }
   
   
