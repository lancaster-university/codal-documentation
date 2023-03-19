
.. _program_listing_file_libraries_codal-microbit-v2_source_compat_MicroBitButton.cpp:

Program Listing for File MicroBitButton.cpp
===========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_compat_MicroBitButton.cpp>` (``libraries/codal-microbit-v2/source/compat/MicroBitButton.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
   The MIT License (MIT)
   
   Copyright (c) 2020 Lancaster University.
   
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
   
   #include "MicroBitButton.h"
   
   using namespace codal;
   
   static PullMode getPullModeFronPinMode(PinMode mode)
   {
       PullMode result = PullMode::None;
   
       if (mode == PinMode::PullDown)
           result = PullMode::Down;
   
       if (mode == PinMode::PullUp)
           result = PullMode::Up;
   
       return result;
   }
   
   MicroBitButton::MicroBitButton(PinName name, uint16_t id, MicroBitButtonEventConfiguration eventConfiguration, PinMode mode) : NRF52Pin(id, name, PIN_CAPABILITY_DIGITAL), Button(*this, id, eventConfiguration, ButtonPolarity::ACTIVE_LOW, getPullModeFronPinMode(mode))
   {
   }
   
   MicroBitButton::MicroBitButton(PinNumber p_number, uint16_t id, MicroBitButtonEventConfiguration eventConfiguration, PinMode mode) : NRF52Pin(id, p_number, PIN_CAPABILITY_DIGITAL), Button(*this, id, eventConfiguration, ButtonPolarity::ACTIVE_LOW, getPullModeFronPinMode(mode))
   {
   }
   
   MicroBitButton::MicroBitButton(Pin &p, uint16_t id, ButtonEventConfiguration eventConfiguration, ButtonPolarity polarity, PullMode mode) : NRF52Pin(id, p.name, PIN_CAPABILITY_DIGITAL), Button(p, id, eventConfiguration, polarity, mode)
   {
   
   }
   
   
