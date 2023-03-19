
.. _program_listing_file_libraries_codal-microbit-v2_source_MicroBitAccelerometer.cpp:

Program Listing for File MicroBitAccelerometer.cpp
==================================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_MicroBitAccelerometer.cpp>` (``libraries/codal-microbit-v2/source/MicroBitAccelerometer.cpp``)

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
   
   #include "MicroBitAccelerometer.h"
   #include "MicroBitIO.h"
   #include "MicroBitEvent.h"
   #include "MicroBitCompat.h"
   #include "MicroBitFiber.h"
   #include "MicroBitDevice.h"
   #include "MicroBitI2C.h"
   #include "MicroBitCompass.h"
   #include "MicroBitError.h"
   #include "LSM303Accelerometer.h"
   #include "LSM303Magnetometer.h"
   
   
   Accelerometer* MicroBitAccelerometer::driver;
   
   MicroBitAccelerometer::MicroBitAccelerometer(MicroBitI2C &i2c, uint16_t id) : Accelerometer(coordinateSpace)
   {
       autoDetect(i2c);
   }
   
   Accelerometer& MicroBitAccelerometer::autoDetect(MicroBitI2C &i2c)
   {
       static bool autoDetectCompleted = false;
       static CoordinateSpace coordinateSpace(SIMPLE_CARTESIAN, true, COORDINATE_SPACE_ROTATED_0);
       static NRF52Pin irq1(ID_PIN_IRQ1, P0_25, PIN_CAPABILITY_AD);
   
       /*
        * In essence, the LSM needs at least 6.4ms from power-up before we can use it.
        * https://github.com/microbit-foundation/codal-microbit/issues/33
        */
       target_wait(10);
   
       // Add pullup resisitor to IRQ line (it's floating ACTIVE LO)
       irq1.getDigitalValue();
       irq1.setPull(PullMode::Up);
       irq1.setActiveLo();
       
       if (!autoDetectCompleted)
       {
           MicroBitAccelerometer::driver = NULL;
           MicroBitCompass::driver       = NULL;
   
           // Now, probe for the LSM303, and if it doesn't reply, panic
           if ( LSM303Accelerometer::isDetected(i2c, 0x32) )
           {
               MicroBitAccelerometer::driver = new LSM303Accelerometer( i2c, irq1, coordinateSpace, 0x32 );
               MicroBitCompass::driver = new LSM303Magnetometer( i2c, irq1, coordinateSpace, 0x3C );
               MicroBitCompass::driver->setAccelerometer( *MicroBitAccelerometer::driver );
           }
   
           autoDetectCompleted = true;
       }
       
       return *driver;
   }
   
   int MicroBitAccelerometer::setPeriod(int period)
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->setPeriod(period);
   }
   
   int MicroBitAccelerometer::getPeriod()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getPeriod();
   }
   
   int MicroBitAccelerometer::setRange(int range)
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->setRange( range );
   }
   
   int MicroBitAccelerometer::getRange()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getRange();
   }
   
   int MicroBitAccelerometer::configure()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->configure();
   }
   
   int MicroBitAccelerometer::requestUpdate()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->requestUpdate();
   }
   
   Sample3D MicroBitAccelerometer::getSample(CoordinateSystem coordinateSystem)
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getSample( coordinateSystem );
   }
   
   Sample3D MicroBitAccelerometer::getSample()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getSample();
   }
   
   int MicroBitAccelerometer::getX()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getX();
   }
   
   int MicroBitAccelerometer::getY()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getY();
   }
   
   int MicroBitAccelerometer::getZ()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getZ();
   }
   
   int MicroBitAccelerometer::getPitch()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getPitch();
   }
   
   float MicroBitAccelerometer::getPitchRadians()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getPitchRadians();
   }
   
   int MicroBitAccelerometer::getRoll()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getRoll();
   }
   
   float MicroBitAccelerometer::getRollRadians()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getRollRadians();
   }
   
   uint16_t MicroBitAccelerometer::getGesture()
   {
       if( driver == NULL )
           target_panic( MicroBitPanic::ACCELEROMETER_ERROR );
       
       return driver->getGesture();
   }
   
   MicroBitAccelerometer::~MicroBitAccelerometer()
   {
   }
