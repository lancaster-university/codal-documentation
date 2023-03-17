uBit.thermometer
================

MicroBitThermometer provides access to the surface temperature of the nrf51822.
The temperature reading therefore is not representative of the ambient temperature,
but rather the temperature relative to the surface temperature of the chip.

However, we can make it representative of the ambient temperature in software
through "calibrating" the thermometer.

Calibration is very simple, and is calculated by giving the current temperature
to the `setCalibration()` member function. From the temperature, an offset is
calculated, and is subsequently used to offset future temperature readings.

Real time updates
^^^^^^^^^^^^^^^^^

When using the standard uBit presentation, the thermometer is continuously updated
in the background using an idle thread (after it is first used), which is executed
whenever the micro:bit has no other tasks to perform.

If there is no scheduler running, the values are synchronously read on `getTemperature()`
calls. Additionally, if you would like to drive thermometer updates manually `updateSample()`
can be used.