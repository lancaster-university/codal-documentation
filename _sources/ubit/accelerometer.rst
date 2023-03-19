uBit.accelerometer
==================

Onboard the micro:bit is an accelerometer, and it is linked to the
[i2c](i2c.md) bus which is used to read data from the accelerometer.

The accelerometer on the micro:bit detects the acceleration (*in milli-g*) in 3 planes: x and y
(*the horizontal planes*), and z (*the vertical plane*).

As well as detecting acceleration, accelerometers can also detect orientation, which
is used in smart phones and tablets to rotate content as you tilt the device. This means
that the micro:bit can infer its own orientation as well!

As well as being used to detect acceleration, accelerometers are also used to detect
the rate of deceleration. A great example of an application of accelerometers are
airbags in modern vehicles, where an accelerometer is used to detect the rapid deceleration
of a vehicle. If rapid deceleration were to occur, the airbags are deployed.

Accelerometers can also be used to detect when an object is in free fall, which is
when only the force gravity is acting upon an object. If you were to throw a ball directly
into the air, free fall would begin as soon as the ball begins its decent after the
acceleration from your throw has subsided.

There are [two variants of the micro:bit](https://tech.microbit.org/hardware/)
, one uses the [MMA8653](../resources/datasheets/MMA8653.pdf) and the other a uses the 
[LSM303](https://www.st.com/resource/en/datasheet/lsm303agr.pdf) combined accelerometer and 
magnetometer.

Real-Time Updates
^^^^^^^^^^^^^^^^^

When using the standard uBit presentation, the accelerometer is continuously updated
in the background using an idle thread (after it is first used), which is executed
whenever the micro:bit has no other tasks to perform..

If there is no scheduler running, the values are synchronously read on `get[X,Y,Z]()`
calls. Additionally, if you would like to drive accelerometer updates manually `updateSample()`
can be used.