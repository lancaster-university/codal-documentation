
.. _program_listing_file_libraries_codal-microbit-v2_source_SoundOutputPin.cpp:

Program Listing for File SoundOutputPin.cpp
===========================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-microbit-v2_source_SoundOutputPin.cpp>` (``libraries/codal-microbit-v2/source/SoundOutputPin.cpp``)

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
   
   #include "SoundOutputPin.h"
   #include "Synthesizer.h"
   #include "CodalDmesg.h"
   #include "MicroBitAudio.h"
   
   using namespace codal;
   
   SoundOutputPin::SoundOutputPin(Mixer2 &mix, int id) : codal::Pin(id, 0, PIN_CAPABILITY_ANALOG), mixer(mix), outputBuffer(SOUND_OUTPUT_PIN_BUFFER_SIZE)
   {
       this->value = 128;
       this->periodUs = 0;
       this->channel = NULL;
       this->timeOfLastUpdate = 0;
       this->bufferWritePos = outputBuffer.getBytes();
       this->position = 0.0f;
       this->volume = 0;
   
       // Enable lazy periodic callback and optimised silence generation.
       CodalComponent::status |= DEVICE_COMPONENT_STATUS_IDLE_TICK;
   }
   
   
   int SoundOutputPin::setAnalogValue(int value)
   {
       if (value < 0 || value > 1024)
           return DEVICE_INVALID_PARAMETER;
   
       // Normalize the duty cycle (we don't care if duty cycle is hi or lo)
       if (value > 512)
           value = 1024 - value;
   
       // Normalize volume to approximately the behaviour of a micro:bit v1 with headphones on edge connector pin 0.
       this->value = min(128, value);
       update();
   
       return DEVICE_OK;
   }
   
   int SoundOutputPin::getAnalogValue()
   {
       return value;
   }
   
   
   int SoundOutputPin::setAnalogPeriodUs(uint32_t period)
   {
       this->periodUs = period;
   
   #if CONFIG_ENABLED(CONFIG_SOUND_OUTPUT_PIN_DISCRETE_OUTPUT)
       // Snap to the nearest clean divisor of our carrier freuency.
       float frequency = CONFIG_MIXER_DEFAULT_SAMPLERATE;
       uint32_t samplePeriodUs = (1000000 / frequency);
   
       // Find the nearest integer value to periodUs that is a divisor of sampleUs
       uint32_t i = period / samplePeriodUs;
   
       uint32_t period1 = i * samplePeriodUs;
       uint32_t period2 = (i+1) * samplePeriodUs;
   
       float error1 = abs((float)period - (float)period1);
       float error2 = abs((float)period - (float)period2);
   
       this->periodUs = (error1 < error2) ? period1 : period2;
   
   #endif
   
       update();
   
       return DEVICE_OK;
   }
   
   int SoundOutputPin::setAnalogPeriod(int period)
   {
       return setAnalogPeriodUs(period*1000);
   }
   
   uint32_t SoundOutputPin::getAnalogPeriodUs()
   {
       return periodUs;
   }
   
   int SoundOutputPin::getAnalogPeriod()
   {
       return getAnalogPeriodUs() / 1000;
   }
   
   void SoundOutputPin::update()
   {
       // Snapshot the curent time, so we can determine periods of silence.
       this->timeOfLastUpdate = system_timer_current_time();
       this->volume = periodUs == 0 ? 0 : value;
   
       updateOutputBuffer();
   
       // If this is the first time we've been asked to produce a sound, connect to the audio mixer pipeline.
       if ((CodalComponent::status & SOUND_OUTPUT_PIN_STATUS_ENABLED) == 0)
       {
           MicroBitAudio::requestActivation();
           channel = mixer.addChannel(*this, SOUND_OUTPUT_PIN_SAMPLE_RATE, 128);
           CodalComponent::status |= SOUND_OUTPUT_PIN_STATUS_ENABLED;
           channel->pullRequest();
       }
   }
   
   void SoundOutputPin::updateOutputBuffer(bool all)
   {
       uint8_t *bufferEnd = outputBuffer.getBytes() + outputBuffer.length();
       uint8_t *endPosition = all ? bufferEnd : outputBuffer.getBytes() + min(outputBuffer.length(), (int) ((1000.0f / SOUND_OUTPUT_PIN_SAMPLE_RATE) * (timeOfLastUpdate - timeOfLastPull)));
   
       // Fill the buffer based on the previously defined period and value settings.
   #if CONFIG_ENABLED(CONFIG_SOUND_OUTPUT_PIN_TONEPRINT)
       float frequency = _periodUs ? 1000000.0f / _periodUs : 0;
       float skip = ((float)(EMOJI_SYNTHESIZER_TONE_WIDTH_F * frequency) / (float)SOUND_OUTPUT_PIN_SAMPLE_RATE);
   
       while(bufferWritePos < endPosition)
       {
           *bufferWritePos = Synthesizer::SquareWaveTone(NULL, (int) position) ? this->volume : 0;
           bufferWritePos++;
           position += skip;
   
           // Keep our toneprint pointer in range
           while(position > EMOJI_SYNTHESIZER_TONE_WIDTH_F)
               position -= EMOJI_SYNTHESIZER_TONE_WIDTH_F;
       }
   
   #else
       uint32_t samplePeriodUs = (1000000 / SOUND_OUTPUT_PIN_SAMPLE_RATE);
       uint32_t skip = _periodUs / samplePeriodUs;
   
       while(bufferWritePos < endPosition)
       {
           *bufferWritePos = position < skip / 2 ? this->volume : 0;
           position++;
   
           // Keep our toneprint pointer in range
           if(position > skip)
               position = 0;
   
           bufferWritePos++;
       }
   #endif
   
       // Snapshot the current sound parameters in case they are changed in flight
       _periodUs = periodUs;
       _value = value;
   }
   
   void SoundOutputPin::idleCallback()
   {
       if ((CodalComponent::status & SOUND_OUTPUT_PIN_STATUS_ACTIVE) && (this->volume == 0) && (system_timer_current_time() - this->timeOfLastUpdate > CONFIG_SOUND_OUTPUT_PIN_SILENCE_GATE))
           CodalComponent::status &= ~SOUND_OUTPUT_PIN_STATUS_ACTIVE;
   
       // If our volume is non-zero and we're not active, then restart to synthesizer.
       if (!(CodalComponent::status & SOUND_OUTPUT_PIN_STATUS_ACTIVE) && this->volume > 0)
           CodalComponent::status |= SOUND_OUTPUT_PIN_STATUS_ACTIVE;
   }
   
   ManagedBuffer SoundOutputPin::pull()
   {
       ManagedBuffer result;
   
       if (CodalComponent::status & SOUND_OUTPUT_PIN_STATUS_ACTIVE)
       {
           result = outputBuffer;
   
           updateOutputBuffer(true);
           outputBuffer = ManagedBuffer(SOUND_OUTPUT_PIN_BUFFER_SIZE);
       }
   
       this->bufferWritePos = outputBuffer.getBytes();
       this->timeOfLastPull = system_timer_current_time();
       channel->pullRequest();
   
       return result;
   }
   
   int SoundOutputPin::getFormat()
   {
       return DATASTREAM_FORMAT_8BIT_UNSIGNED;
   }
   
   bool SoundOutputPin::isConnected()
   {
       return this->channel != NULL;
   }
