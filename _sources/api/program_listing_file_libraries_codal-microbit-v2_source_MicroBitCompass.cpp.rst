
.. _program_listing_file_libraries_codal-microbit-v2_source_MicroBitCompass.cpp:

Program Listing for File MicroBitCompass.cpp
============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_MicroBitCompass.cpp>` (``libraries/codal-microbit-v2/source/MicroBitCompass.cpp``)

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
   
   #include "MicroBitCompass.h"
   #include "ErrorNo.h"
   #include "MicroBitEvent.h"
   #include "MicroBitCompat.h"
   #include "MicroBitFiber.h"
   #include "MicroBitDevice.h"
   #include "MicroBitError.h"
   #include "LSM303Magnetometer.h"
   
   Compass* MicroBitCompass::driver;
   
   MicroBitCompass::MicroBitCompass(MicroBitI2C &i2c, uint16_t id) : Compass(MicroBitAccelerometer::coordinateSpace)
   {
       autoDetect(i2c);
   }
   
   Compass& MicroBitCompass::autoDetect(MicroBitI2C &i2c)
   {
       /*
        * In essence, the LSM needs at least 6.4ms from power-up before we can use it.
        * https://github.com/microbit-foundation/codal-microbit/issues/33
        */
       target_wait(10);
   
       // We only have combined sensors, so rely on the accelerometer detection code to also detect the magnetomter.
       MicroBitAccelerometer::autoDetect(i2c);
   
       return *MicroBitCompass::driver;
   }
   
   int MicroBitCompass::heading()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
   
       return driver->heading();
   }
   
   int MicroBitCompass::getFieldStrength()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->getFieldStrength();
   }
   
   int MicroBitCompass::calibrate()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->calibrate();
   }
   
   void MicroBitCompass::setCalibration(CompassCalibration calibration)
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->setCalibration( calibration );
   }
   
   CompassCalibration MicroBitCompass::getCalibration()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->getCalibration();
   }
   
   int MicroBitCompass::isCalibrated()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->isCalibrated();
   }
   
   int MicroBitCompass::isCalibrating()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->isCalibrating();
   }
   
   void MicroBitCompass::clearCalibration()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->clearCalibration();
   }
   
   int MicroBitCompass::configure()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->configure();
   }
   
   void MicroBitCompass::setAccelerometer(MicroBitAccelerometer &accelerometer)
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->setAccelerometer( accelerometer );
   }
   
   int MicroBitCompass::setPeriod(int period)
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->setPeriod( period );
   }
   
   int MicroBitCompass::getPeriod()
   {
       return driver->getPeriod();
   }
   
   int MicroBitCompass::requestUpdate()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->requestUpdate();
   }
   
   Sample3D MicroBitCompass::getSample(CoordinateSystem coordinateSystem)
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->getSample( coordinateSystem );
   }
   
   Sample3D MicroBitCompass::getSample()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->getSample();
   }
   
   int MicroBitCompass::getX()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->getX();
   }
   
   int MicroBitCompass::getY()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->getY();
   }
   
   int MicroBitCompass::getZ()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::COMPASS_ERROR );
       
       return driver->getZ();
   }
   
   MicroBitCompass::~MicroBitCompass()
   {
   }
   
