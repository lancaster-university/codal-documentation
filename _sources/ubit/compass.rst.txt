uBit.compass
============

Onboard the micro:bit is an electronic magnetometer. Like the [accelerometer](accelerometer.md), the  
magnetometer is linked to the [i2c](i2c.md) bus, which is used to access data
on the magnetometer.

The magnetometer provides information about the magnetic field where a micro:bit
is situated, crucially providing an indication of where magnetic North is located.

Raw magnetic field information alone is not enough to provide accurate
compass headings. Therefore, the [accelerometer](accelerometer.md) is used in
conjunction with the magnetometer to reduce the inaccuracy of the magnetometer reading.

The magnetometer is inaccurate because it considers all 3 planes: x, y and z.
The heading North only exists in the horizontal planes (x and y), therefore we only
need values in these planes. The accelerometer is used to filter out the vertical plane (z)
to make our headings far more accurate. You can see this in action when calibrating the compass.

After calibration has been performed, the end product is an e-compass!

There are [two variants of the micro:bit](https://tech.microbit.org/hardware/)
, one uses the NXP [MAG3110](../resources/datasheets/MAG3110.pdf) and the other a uses the ST
[LSM303](https://www.st.com/resource/en/datasheet/lsm303agr.pdf) combined accelerometer and
magnetometer.

Real-Time Updates
^^^^^^^^^^^^^^^^^

When using the standard uBit presentation, the compass is continuously updated
in the background using an idle thread (after it is first used), which is executed
whenever the micro:bit has no other tasks to perform.

If there is no scheduler running, the values are synchronously read on `get[X,Y,Z]()` and `heading()`
calls. Additionally, if you would like to drive compass updates manually `updateSample()`
can be used.

Read Current Values
^^^^^^^^^^^^^^^^^^^

.. doxygenfunction:: codal::Compass::getSample()
.. doxygenfunction:: codal::Compass::getX
.. doxygenfunction:: codal::Compass::getY
.. doxygenfunction:: codal::Compass::getZ
.. doxygenfunction:: codal::Compass::heading
.. doxygenfunction:: codal::Compass::basicBearing
.. doxygenfunction:: codal::Compass::tiltCompensatedBearing
.. doxygenfunction:: codal::Compass::getFieldStrength

Calibration
^^^^^^^^^^^

The compass is a particularly sensitive device, and can be affected by very weak magnetic fields nearby. To
avoid this, the compass can be calibrated and under normal operation, the micro:bit will attempt to perform
a calibration cycle whenever the calibration information is too old or missing.

.. note::
    The compass driver will only calibrate itself automatically if the user program uses the compass.

.. doxygenfunction:: codal::Compass::calibrate
.. doxygenfunction:: codal::Compass::isCalibrating
.. doxygenfunction:: codal::Compass::clearCalibration

Requesting Data
^^^^^^^^^^^^^^^

.. note::
    Most of the time, these are not needed for the compass to function correctly, as this is handled automatically
    by the uBit object on initialisation.

.. doxygenfunction:: codal::Compass::requestUpdate
.. doxygenfunction:: codal::Compass::update
.. doxygenfunction:: codal::Compass::setPeriod
.. doxygenfunction:: codal::Compass::getPeriod