
.. _program_listing_file_libraries_codal-core_source_drivers_AnimatedDisplay.cpp:

Program Listing for File AnimatedDisplay.cpp
============================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_AnimatedDisplay.cpp>` (``libraries/codal-core/source/drivers/AnimatedDisplay.cpp``)

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
   
   #include "AnimatedDisplay.h"
   #include "CodalFiber.h"
   #include "NotifyEvents.h"
   #include "CodalDmesg.h"
   
   using namespace codal;
   
   AnimatedDisplay::AnimatedDisplay(Display& _display, uint16_t id) : display(_display), font(), printingText(), scrollingImage()
   {
       this->id = id;
       this->status = 0;
   
       status |= DEVICE_COMPONENT_STATUS_SYSTEM_TICK;
       status |= DEVICE_COMPONENT_RUNNING;
   
       animationMode = AnimationMode::ANIMATION_MODE_NONE;
       animationDelay = 0;
       animationTick = 0;
       scrollingChar = 0;
       scrollingPosition = 0;
       printingChar = 0;
       scrollingImagePosition = 0;
       scrollingImageStride = 0;
       scrollingImageRendered = false;
   }
   
   void AnimatedDisplay::animationUpdate()
   {
       // If there's no ongoing animation, then nothing to do.
       if (animationMode == ANIMATION_MODE_NONE)
           return;
   
       animationTick += (SCHEDULER_TICK_PERIOD_US/1000);
   
       if(animationTick >= animationDelay)
       {
           animationTick = 0;
   
           if (animationMode == ANIMATION_MODE_SCROLL_TEXT)
               this->updateScrollText();
   
           if (animationMode == ANIMATION_MODE_PRINT_TEXT)
               this->updatePrintText();
   
           if (animationMode == ANIMATION_MODE_SCROLL_IMAGE)
               this->updateScrollImage();
   
           if (animationMode == ANIMATION_MODE_ANIMATE_IMAGE || animationMode == ANIMATION_MODE_ANIMATE_IMAGE_WITH_CLEAR)
               this->updateAnimateImage();
   
           if(animationMode == ANIMATION_MODE_PRINT_CHARACTER)
           {
               animationMode = ANIMATION_MODE_NONE;
               this->sendAnimationCompleteEvent();
           }
       }
   }
   
   void AnimatedDisplay::sendAnimationCompleteEvent()
   {
       // Signal that we've completed an animation.
       Event(id, DISPLAY_EVT_ANIMATION_COMPLETE);
   
       // Wake up a fiber that was blocked on the animation (if any).
       Event(DEVICE_ID_NOTIFY_ONE, DISPLAY_EVT_FREE);
   }
   
   void AnimatedDisplay::updateScrollText()
   {
       display.image.shiftLeft(1);
   
       if (scrollingPosition < BITMAP_FONT_WIDTH && scrollingChar < scrollingText.length())
       {
           const uint8_t *v = font.get(scrollingText.charAt(scrollingChar));
           uint8_t mask = 1 << (BITMAP_FONT_WIDTH - scrollingPosition - 1);
           uint8_t x = display.getWidth()-1;
   
           for (int y=0; y<BITMAP_FONT_HEIGHT; y++)
           {
               if (*v & mask)
                   display.image.setPixelValue(x, y, 255);
   
               v++;
           }
       }
   
       scrollingPosition++;
   
       if (scrollingPosition == display.getWidth() + DISPLAY_SPACING)
       {
           scrollingPosition = 0;
   
           if (scrollingChar >= scrollingText.length())
           {
               animationMode = ANIMATION_MODE_NONE;
               this->sendAnimationCompleteEvent();
               return;
           }
           scrollingChar++;
       }
   }
   
   void AnimatedDisplay::updatePrintText()
   {
       display.image.print(printingChar < printingText.length() ? printingText.charAt(printingChar) : ' ',0,0);
   
       if (printingChar > printingText.length())
       {
           animationMode = ANIMATION_MODE_NONE;
   
           this->sendAnimationCompleteEvent();
           return;
       }
   
       printingChar++;
   }
   
   void AnimatedDisplay::updateScrollImage()
   {
       display.image.clear();
   
       if (((display.image.paste(scrollingImage, scrollingImagePosition, 0, 0) == 0) && scrollingImageRendered) || scrollingImageStride == 0)
       {
           animationMode = ANIMATION_MODE_NONE;
           this->sendAnimationCompleteEvent();
   
           return;
       }
   
       scrollingImagePosition += scrollingImageStride;
       scrollingImageRendered = true;
   }
   
   void AnimatedDisplay::updateAnimateImage()
   {
       //wait until we have rendered the last position to give a continuous animation.
       if (scrollingImagePosition <= -scrollingImage.getWidth() + (display.getWidth() + scrollingImageStride) && scrollingImageRendered)
       {
           if (animationMode == ANIMATION_MODE_ANIMATE_IMAGE_WITH_CLEAR)
               display.image.clear();
   
           animationMode = ANIMATION_MODE_NONE;
   
           this->sendAnimationCompleteEvent();
           return;
       }
   
       if(scrollingImagePosition > 0)
           display.image.shiftLeft(-scrollingImageStride);
   
       display.image.paste(scrollingImage, scrollingImagePosition, 0, 0);
   
       if(scrollingImageStride == 0)
       {
           animationMode = ANIMATION_MODE_NONE;
           this->sendAnimationCompleteEvent();
       }
   
       scrollingImageRendered = true;
   
       scrollingImagePosition += scrollingImageStride;
   }
   
   void AnimatedDisplay::stopAnimation()
   {
       // Reset any ongoing animation.
       if (animationMode != ANIMATION_MODE_NONE)
       {
           animationMode = ANIMATION_MODE_NONE;
   
           // Indicate that we've completed an animation.
           Event(id,DISPLAY_EVT_ANIMATION_COMPLETE);
   
           // Wake up aall fibers that may blocked on the animation (if any).
           Event(DEVICE_ID_NOTIFY, DISPLAY_EVT_FREE);
       }
   
       // Clear the display and setup the animation timers.
       this->display.image.clear();
   }
   
   void AnimatedDisplay::waitForFreeDisplay()
   {
       // If there's an ongoing animation, wait for our turn to display.
       while (animationMode != ANIMATION_MODE_NONE && animationMode != ANIMATION_MODE_STOPPED)
           fiber_wait_for_event(DEVICE_ID_NOTIFY, DISPLAY_EVT_FREE);
   }
   
   void AnimatedDisplay::fiberWait()
   {
       if (fiber_wait_for_event(DEVICE_ID_DISPLAY, DISPLAY_EVT_ANIMATION_COMPLETE) == DEVICE_NOT_SUPPORTED)
           while(animationMode != ANIMATION_MODE_NONE && animationMode != ANIMATION_MODE_STOPPED)
               target_wait_for_event();
   }
   
   int AnimatedDisplay::printCharAsync(char c, int delay)
   {
       //sanitise this value
       if(delay < 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If the display is free, it's our turn to display.
       if (animationMode == ANIMATION_MODE_NONE || animationMode == ANIMATION_MODE_STOPPED)
       {
           display.image.print(c, 0, 0);
   
           if (delay > 0)
           {
               animationDelay = delay;
               animationTick = 0;
               animationMode = ANIMATION_MODE_PRINT_CHARACTER;
           }
       }
       else
       {
           return DEVICE_BUSY;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::printAsync(ManagedString s, int delay)
   {
       if (s.length() == 1)
           return printCharAsync(s.charAt(0));
   
       //sanitise this value
       if (delay <= 0 )
           return DEVICE_INVALID_PARAMETER;
   
       if (animationMode == ANIMATION_MODE_NONE || animationMode == ANIMATION_MODE_STOPPED)
       {
           printingChar = 0;
           printingText = s;
           animationDelay = delay;
           animationTick = 0;
   
           animationMode = ANIMATION_MODE_PRINT_TEXT;
       }
       else
       {
           return DEVICE_BUSY;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::printAsync(Image i, int x, int y, int alpha, int delay)
   {
       if(delay < 0)
           return DEVICE_INVALID_PARAMETER;
   
       if (animationMode == ANIMATION_MODE_NONE || animationMode == ANIMATION_MODE_STOPPED)
       {
           display.image.paste(i, x, y, alpha);
   
           if(delay > 0)
           {
               animationDelay = delay;
               animationTick = 0;
               animationMode = ANIMATION_MODE_PRINT_CHARACTER;
           }
       }
       else
       {
           return DEVICE_BUSY;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::printChar(char c, int delay)
   {
       if (delay < 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If there's an ongoing animation, wait for our turn to display.
       this->waitForFreeDisplay();
   
       // If the display is free, it's our turn to display.
       // If someone called stopAnimation(), then we simply skip...
       if (animationMode == ANIMATION_MODE_NONE)
       {
           this->printCharAsync(c, delay);
   
           if (delay > 0)
               fiberWait();
       }
       else
       {
           return DEVICE_CANCELLED;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::print(ManagedString s, int delay)
   {
       //sanitise this value
       if(delay <= 0 )
           return DEVICE_INVALID_PARAMETER;
   
       // If there's an ongoing animation, wait for our turn to display.
       this->waitForFreeDisplay();
   
       // If the display is free, it's our turn to display.
       // If someone called stopAnimation(), then we simply skip...
       if (animationMode == ANIMATION_MODE_NONE)
       {
           if (s.length() == 1)
           {
               return printCharAsync(s.charAt(0));
           }
           else
           {
               this->printAsync(s, delay);
               fiberWait();
           }
       }
       else
       {
           return DEVICE_CANCELLED;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::print(Image i, int x, int y, int alpha, int delay)
   {
       if(delay < 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If there's an ongoing animation, wait for our turn to display.
       this->waitForFreeDisplay();
   
       // If the display is free, it's our turn to display.
       // If someone called stopAnimation(), then we simply skip...
       if (animationMode == ANIMATION_MODE_NONE)
       {
           this->printAsync(i, x, y, alpha, delay);
   
           if (delay > 0)
               fiberWait();
       }
       else
       {
           return DEVICE_CANCELLED;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::scrollAsync(ManagedString s, int delay)
   {
       //sanitise this value
       if(delay <= 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If the display is free, it's our turn to display.
       if (animationMode == ANIMATION_MODE_NONE || animationMode == ANIMATION_MODE_STOPPED)
       {
           scrollingPosition = 0;
           scrollingChar = 0;
           scrollingText = s;
   
           animationDelay = delay;
           animationTick = 0;
           animationMode = ANIMATION_MODE_SCROLL_TEXT;
       }
       else
       {
           return DEVICE_BUSY;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::scrollAsync(Image image, int delay, int stride)
   {
       //sanitise the delay value
       if(delay <= 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If the display is free, it's our turn to display.
       if (animationMode == ANIMATION_MODE_NONE || animationMode == ANIMATION_MODE_STOPPED)
       {
           scrollingImagePosition = stride < 0 ? display.getWidth() : -image.getWidth();
           scrollingImageStride = stride;
           scrollingImage = image;
           scrollingImageRendered = false;
   
           animationDelay = stride == 0 ? 0 : delay;
           animationTick = 0;
           animationMode = ANIMATION_MODE_SCROLL_IMAGE;
       }
       else
       {
           return DEVICE_BUSY;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::scroll(ManagedString s, int delay)
   {
       //sanitise this value
       if(delay <= 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If there's an ongoing animation, wait for our turn to display.
       this->waitForFreeDisplay();
   
       // If the display is free, it's our turn to display.
       // If someone called stopAnimation(), then we simply skip...
       if (animationMode == ANIMATION_MODE_NONE)
       {
           // Start the effect.
           this->scrollAsync(s, delay);
   
           // Wait for completion.
           fiberWait();
       }
       else
       {
           return DEVICE_CANCELLED;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::scroll(Image image, int delay, int stride)
   {
       //sanitise the delay value
       if(delay <= 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If there's an ongoing animation, wait for our turn to display.
       this->waitForFreeDisplay();
   
       // If the display is free, it's our turn to display.
       // If someone called stopAnimation(), then we simply skip...
       if (animationMode == ANIMATION_MODE_NONE)
       {
           // Start the effect.
           this->scrollAsync(image, delay, stride);
   
           // Wait for completion.
           fiberWait();
       }
       else
       {
           return DEVICE_CANCELLED;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::animateAsync(Image image, int delay, int stride, int startingPosition, int autoClear)
   {
       //sanitise the delay value
       if(delay <= 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If the display is free, we can display.
       if (animationMode == ANIMATION_MODE_NONE || animationMode == ANIMATION_MODE_STOPPED)
       {
           // Assume right to left functionality, to align with scrollString()
           stride = -stride;
   
           //calculate starting position which is offset by the stride
           scrollingImagePosition = (startingPosition == DISPLAY_ANIMATE_DEFAULT_POS) ? display.getWidth() + stride : startingPosition;
           scrollingImageStride = stride;
           scrollingImage = image;
           scrollingImageRendered = false;
   
           animationDelay = stride == 0 ? 0 : delay;
           animationTick = delay-1;
           animationMode = autoClear ? ANIMATION_MODE_ANIMATE_IMAGE_WITH_CLEAR : ANIMATION_MODE_ANIMATE_IMAGE;
       }
       else
       {
           return DEVICE_BUSY;
       }
   
       return DEVICE_OK;
   }
   
   int AnimatedDisplay::animate(Image image, int delay, int stride, int startingPosition, int autoClear)
   {
       //sanitise the delay value
       if(delay <= 0)
           return DEVICE_INVALID_PARAMETER;
   
       // If there's an ongoing animation, wait for our turn to display.
       this->waitForFreeDisplay();
   
       // If the display is free, it's our turn to display.
       // If someone called stopAnimation(), then we simply skip...
       if (animationMode == ANIMATION_MODE_NONE)
       {
           // Start the effect.
           this->animateAsync(image, delay, stride, startingPosition, autoClear);
   
           // Wait for completion.
           //TODO: Put this in when we merge tight-validation
           //if (delay > 0)
               fiberWait();
       }
       else
       {
           return DEVICE_CANCELLED;
       }
   
       return DEVICE_OK;
   }
   
   
   void AnimatedDisplay::periodicCallback()
   {
       this->animationUpdate();
   }
   
   AnimatedDisplay::~AnimatedDisplay()
   {
       status &= ~DEVICE_COMPONENT_STATUS_SYSTEM_TICK;
   }
