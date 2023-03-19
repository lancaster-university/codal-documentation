
.. _program_listing_file_libraries_codal-microbit-v2_source_bluetooth_MicroBitTemperatureService.cpp:

Program Listing for File MicroBitTemperatureService.cpp
=======================================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_bluetooth_MicroBitTemperatureService.cpp>` (``libraries/codal-microbit-v2/source/bluetooth/MicroBitTemperatureService.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   
   Copyright (c) 2016 British Broadcasting Corporation.
   This software is provided by Lancaster University by arrangement with the BBC.
   
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
   
   #include "MicroBitConfig.h"
   
   #if CONFIG_ENABLED(DEVICE_BLE)
   
   #include "MicroBitTemperatureService.h"
   
   
   const uint16_t MicroBitTemperatureService::serviceUUID               = 0x6100;
   const uint16_t MicroBitTemperatureService::charUUID[ mbbs_cIdxCOUNT] = { 0x9250, 0x1b25 };
   
   
   MicroBitTemperatureService::MicroBitTemperatureService( BLEDevice &_ble, MicroBitThermometer &_thermometer) :
       thermometer(_thermometer)
   {
       // Initialise our characteristic values.
       temperatureDataCharacteristicBuffer   = 0;
       temperaturePeriodCharacteristicBuffer = 0;
       
       // Register the base UUID and create the service.
       RegisterBaseUUID( bs_base_uuid);
       CreateService( serviceUUID);
   
       // Create the data structures that represent each of our characteristics in Soft Device.
       CreateCharacteristic( mbbs_cIdxDATA, charUUID[ mbbs_cIdxDATA],
                            (uint8_t *)&temperatureDataCharacteristicBuffer,
                            sizeof(temperatureDataCharacteristicBuffer), sizeof(temperatureDataCharacteristicBuffer),
                            microbit_propREAD | microbit_propNOTIFY);
   
       CreateCharacteristic( mbbs_cIdxPERIOD, charUUID[ mbbs_cIdxPERIOD],
                            (uint8_t *)&temperaturePeriodCharacteristicBuffer,
                            sizeof(temperaturePeriodCharacteristicBuffer), sizeof(temperaturePeriodCharacteristicBuffer),
                            microbit_propREAD | microbit_propWRITE);
   
       if ( getConnected())
           listen( true);
   }
   
   
   void MicroBitTemperatureService::listen( bool yes)
   {
       if (EventModel::defaultEventBus)
       {
           if ( yes)
           {
               // Ensure thermometer is being updated
               temperatureDataCharacteristicBuffer   = thermometer.getTemperature();
               temperaturePeriodCharacteristicBuffer = thermometer.getPeriod();
               EventModel::defaultEventBus->listen(MICROBIT_ID_THERMOMETER, MICROBIT_THERMOMETER_EVT_UPDATE, this, &MicroBitTemperatureService::temperatureUpdate, MESSAGE_BUS_LISTENER_IMMEDIATE);
           }
           else
           {
               EventModel::defaultEventBus->ignore(MICROBIT_ID_THERMOMETER, MICROBIT_THERMOMETER_EVT_UPDATE, this, &MicroBitTemperatureService::temperatureUpdate);
           }
       }
   }
   
   
   void MicroBitTemperatureService::onConnect( const microbit_ble_evt_t *p_ble_evt)
   {
       listen( true);
   }
   
   
   void MicroBitTemperatureService::onDisconnect( const microbit_ble_evt_t *p_ble_evt)
   {
       listen( false);
   }
   
   
   void MicroBitTemperatureService::onDataWritten(const microbit_ble_evt_write_t *params)
   {
       if (params->handle == valueHandle( mbbs_cIdxPERIOD) && params->len >= sizeof(temperaturePeriodCharacteristicBuffer))
       {
           memcpy(&temperaturePeriodCharacteristicBuffer, params->data, sizeof(temperaturePeriodCharacteristicBuffer));
           thermometer.setPeriod(temperaturePeriodCharacteristicBuffer);
   
           // The accelerometer will choose the nearest period to that requested that it can support
           // Read back the ACTUAL period it is using, and report this back.
           temperaturePeriodCharacteristicBuffer = thermometer.getPeriod();
           setChrValue( mbbs_cIdxPERIOD, (const uint8_t *)&temperaturePeriodCharacteristicBuffer, sizeof(temperaturePeriodCharacteristicBuffer));
       }
   }
   
   
   void MicroBitTemperatureService::temperatureUpdate(MicroBitEvent)
   {
       if ( getConnected())
       {
           temperatureDataCharacteristicBuffer = thermometer.getTemperature();
           notifyChrValue( mbbs_cIdxDATA, (uint8_t *)&temperatureDataCharacteristicBuffer, sizeof(temperatureDataCharacteristicBuffer));
       }
   }
   
   #endif
