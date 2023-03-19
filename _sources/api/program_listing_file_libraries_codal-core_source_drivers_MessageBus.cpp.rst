
.. _program_listing_file_libraries_codal-core_source_drivers_MessageBus.cpp:

Program Listing for File MessageBus.cpp
=======================================

|exhale_lsh| :ref:`Return to documentation for file <file_libraries_codal-core_source_drivers_MessageBus.cpp>` (``libraries/codal-core/source/drivers/MessageBus.cpp``)

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
   
   #include "CodalConfig.h"
   #include "MessageBus.h"
   #include "CodalFiber.h"
   #include "CodalDmesg.h"
   #include "ErrorNo.h"
   #include "NotifyEvents.h"
   #include "codal_target_hal.h"
   
   using namespace codal;
   
   static uint16_t userNotifyId = DEVICE_NOTIFY_USER_EVENT_BASE;
   
   MessageBus::MessageBus()
   {
       this->listeners = NULL;
       this->evt_queue_head = NULL;
       this->evt_queue_tail = NULL;
       this->queueLength = 0;
   
       // ANY listeners for scheduler events MUST be immediate, or else they will not be registered.
       listen(DEVICE_ID_SCHEDULER, DEVICE_SCHEDULER_EVT_IDLE, this, &MessageBus::idle, MESSAGE_BUS_LISTENER_IMMEDIATE);
   
       if(EventModel::defaultEventBus == NULL)
           EventModel::defaultEventBus = this;
   }
   
   REAL_TIME_FUNC
   void async_callback(void *param)
   {
       Listener *listener = (Listener *)param;
   
       // OK, now we need to decide how to behave depending on our configuration.
       // If this a fiber f already active within this listener then check our
       // configuration to determine the correct course of action.
       //
   
       if (listener->flags & MESSAGE_BUS_LISTENER_BUSY)
       {
           // Drop this event, if that's how we've been configured.
           if (listener->flags & MESSAGE_BUS_LISTENER_DROP_IF_BUSY)
               return;
   
           // Queue this event up for later, if that's how we've been configured.
           if (listener->flags & MESSAGE_BUS_LISTENER_QUEUE_IF_BUSY)
           {
               listener->queue(listener->evt);
               return;
           }
       }
   
       // Determine the calling convention for the callback, and invoke...
       // C++ is really bad at this! Especially as the ARM compiler is yet to support C++ 11 :-/
   
       // Record that we have a fiber going into this listener...
       listener->flags |= MESSAGE_BUS_LISTENER_BUSY;
   
       while (1)
       {
           // Firstly, check for a method callback into an object.
           if (listener->flags & MESSAGE_BUS_LISTENER_METHOD)
               listener->cb_method->fire(listener->evt);
   
           // Now a parameterised C function
           else if (listener->flags & MESSAGE_BUS_LISTENER_PARAMETERISED)
               listener->cb_param(listener->evt, listener->cb_arg);
   
           // We must have a plain C function
           else
               listener->cb(listener->evt);
   
   
           // If there are more events to process, dequeue the next one and process it.
           if ((listener->flags & MESSAGE_BUS_LISTENER_QUEUE_IF_BUSY) && listener->evt_queue)
           {
               EventQueueItem *item = listener->evt_queue;
   
               listener->evt = item->evt;
               listener->evt_queue = listener->evt_queue->next;
               delete item;
   
               // We spin the scheduler here, to preven any particular event handler from continuously holding onto resources.
               schedule();
           }
           else
               break;
       }
   
       // The fiber of exiting... clear our state.
       listener->flags &= ~MESSAGE_BUS_LISTENER_BUSY;
   }
   
   REAL_TIME_FUNC
   void MessageBus::queueEvent(Event &evt)
   {
       int processingComplete;
   
       EventQueueItem *prev = evt_queue_tail;
   
       // Now process all handler regsitered as URGENT.
       // These pre-empt the queue, and are useful for fast, high priority services.
       processingComplete = this->process(evt, true);
   
       // If we've already processed all event handlers, we're all done.
       // No need to queue the event.
       if (processingComplete)
           return;
   
       // If we need to queue, but there is no space, then there's nothg we can do.
       if (queueLength >= MESSAGE_BUS_LISTENER_MAX_QUEUE_DEPTH)
       {
           // Note that this can lead to strange lockups, where we await an event that never arrives.
           DMESG("evt %d/%d: overflow!", evt.source, evt.value);
           return;
       }
   
       // Otherwise, we need to queue this event for later processing...
       // We queue this event at the tail of the queue at the point where we entered queueEvent()
       // This is important as the processing above *may* have generated further events, and
       // we want to maintain ordering of events.
       EventQueueItem *item = new EventQueueItem(evt);
   
       // The queue was empty when we entered this function, so queue our event at the start of the queue.
       target_disable_irq();
   
       if (prev == NULL)
       {
           item->next = evt_queue_head;
           evt_queue_head = item;
       }
       else
       {
           item->next = prev->next;
           prev->next = item;
       }
   
       if (item->next == NULL)
           evt_queue_tail = item;
   
       queueLength++;
   
       target_enable_irq();
   }
   
   REAL_TIME_FUNC
   EventQueueItem* MessageBus::dequeueEvent()
   {
       EventQueueItem *item = NULL;
   
       target_disable_irq();
   
       if (evt_queue_head != NULL)
       {
           item = evt_queue_head;
           evt_queue_head = item->next;
   
           if (evt_queue_head == NULL)
               evt_queue_tail = NULL;
   
           queueLength--;
       }
   
       target_enable_irq();
   
   
       return item;
   }
   
   int MessageBus::deleteMarkedListeners()
   {
       Listener *l, *p;
       int removed = 0;
   
       l = listeners;
       p = NULL;
   
       // Walk this list of event handlers. Delete any that match the given listener.
       while (l != NULL)
       {
           if ((l->flags & MESSAGE_BUS_LISTENER_DELETING) && !(l->flags & MESSAGE_BUS_LISTENER_BUSY))
           {
               if (p == NULL)
                   listeners = l->next;
               else
                   p->next = l->next;
   
               // delete the listener.
               Listener *t = l;
               l = l->next;
   
               delete t;
               removed++;
   
               continue;
           }
   
           p = l;
           l = l->next;
       }
   
       return removed;
   }
   
   void MessageBus::idle(Event)
   {
       // Clear out any listeners marked for deletion
       this->deleteMarkedListeners();
   
       EventQueueItem *item = this->dequeueEvent();
   
       // Whilst there are events to process and we have no useful other work to do, pull them off the queue and process them.
       while (item)
       {
           // send the event to all standard event listeners.
           this->process(item->evt);
   
           // Free the queue item.
           delete item;
   
           // If we have created some useful work to do, we stop processing.
           // This helps to minimise the number of blocked fibers we create at any point in time, therefore
           // also reducing the RAM footprint.
           if(!scheduler_runqueue_empty())
               break;
   
           // Pull the next event to process, if there is one.
           item = this->dequeueEvent();
       }
   }
   
   REAL_TIME_FUNC
   int MessageBus::send(Event evt)
   {
       // We simply queue processing of the event until we're scheduled in normal thread context.
       // We do this to avoid the possibility of executing event handler code in IRQ context, which may bring
       // hidden race conditions to kids code. Queuing all events ensures causal ordering (total ordering in fact).
       this->queueEvent(evt);
       return DEVICE_OK;
   }
   
   REAL_TIME_FUNC
   int MessageBus::process(Event &evt, bool urgent)
   {
       Listener *l;
       int complete = 1;
       bool listenerUrgent;
   
       l = listeners;
   
       while (l != NULL)
       {
           if((l->id == evt.source || l->id == DEVICE_ID_ANY) && (l->value == evt.value || l->value == DEVICE_EVT_ANY))
           {
               // If we're running under the fiber scheduler, then derive the THREADING_MODE for the callback based on the
               // metadata in the listener itself.
               if (fiber_scheduler_running())
                   listenerUrgent = (l->flags & MESSAGE_BUS_LISTENER_IMMEDIATE) == MESSAGE_BUS_LISTENER_IMMEDIATE;
               else
                   listenerUrgent = true;
   
               // If we should process this event hander in this pass, then activate the listener.
               if(listenerUrgent == urgent && !(l->flags & MESSAGE_BUS_LISTENER_DELETING))
               {
                   l->evt = evt;
   
                   // OK, if this handler has regisitered itself as non-blocking, we just execute it directly...
                   // This is normally only done for trusted system components.
                   // Otherwise, we invoke it in a 'fork on block' context, that will automatically create a fiber
                   // should the event handler attempt a blocking operation, but doesn't have the overhead
                   // of creating a fiber needlessly. (cool huh?)
                   if (l->flags & MESSAGE_BUS_LISTENER_NONBLOCKING || !fiber_scheduler_running())
                       async_callback(l);
                   else
                       invoke(async_callback, l);
               }
               else
                   complete = 0;
           }
   
           l = l->next;
       }
   
       //Serial.println("EXIT");
       //while (!(UCSR0A & _BV(TXC0)));
   
       return complete;
   }
   
   int MessageBus::add(Listener *newListener)
   {
       Listener *l, *p;
       int methodCallback;
   
       //handler can't be NULL!
       if (newListener == NULL)
           return DEVICE_INVALID_PARAMETER;
   
       l = listeners;
   
       // Firstly, we treat a listener as an idempotent operation. Ensure we don't already have this handler
       // registered in a that will already capture these events. If we do, silently ignore.
   
       // We always check the ID, VALUE and CB_METHOD fields.
       // If we have a callback to a method, check the cb_method class. Otherwise, the cb function point is sufficient.
       while (l != NULL)
       {
           methodCallback = (newListener->flags & MESSAGE_BUS_LISTENER_METHOD) && (l->flags & MESSAGE_BUS_LISTENER_METHOD);
   
           if (l->id == newListener->id && l->value == newListener->value && (methodCallback ? *l->cb_method == *newListener->cb_method : l->cb == newListener->cb) && newListener->cb_arg == l->cb_arg)
           {
               // We have a perfect match for this event listener already registered.
               // If it's marked for deletion, we simply resurrect the listener, and we're done.
               // Either way, we return an error code, as the *new* listener should be released...
               if(l->flags & MESSAGE_BUS_LISTENER_DELETING)
                   l->flags &= ~MESSAGE_BUS_LISTENER_DELETING;
   
               return DEVICE_NOT_SUPPORTED;
           }
   
           l = l->next;
       }
   
       // We have a valid, new event handler. Add it to the list.
       // if listeners is null - we can automatically add this listener to the list at the beginning...
       if (listeners == NULL)
       {
           listeners = newListener;
           Event(DEVICE_ID_MESSAGE_BUS_LISTENER, newListener->id);
   
           return DEVICE_OK;
       }
   
       // We maintain an ordered list of listeners.
       // The chain is held stictly in increasing order of ID (first level), then value code (second level).
       // Find the correct point in the chain for this event.
       // Adding a listener is a rare occurance, so we just walk the list...
   
       p = listeners;
       l = listeners;
   
       while (l != NULL && l->id < newListener->id)
       {
           p = l;
           l = l->next;
       }
   
       while (l != NULL && l->id == newListener->id && l->value < newListener->value)
       {
           p = l;
           l = l->next;
       }
   
       //add at front of list
       if (p == listeners && (newListener->id < p->id || (p->id == newListener->id && p->value > newListener->value)))
       {
           newListener->next = p;
   
           //this new listener is now the front!
           listeners = newListener;
       }
   
       //add after p
       else
       {
           newListener->next = p->next;
           p->next = newListener;
       }
   
       Event(DEVICE_ID_MESSAGE_BUS_LISTENER, newListener->id);
       return DEVICE_OK;
   }
   
   int MessageBus::remove(Listener *listener)
   {
       Listener *l;
       int removed = 0;
   
       //handler can't be NULL!
       if (listener == NULL)
           return DEVICE_INVALID_PARAMETER;
   
       l = listeners;
   
       // Walk this list of event handlers. Delete any that match the given listener.
       while (l != NULL)
       {
           if ((listener->flags & MESSAGE_BUS_LISTENER_METHOD) == (l->flags & MESSAGE_BUS_LISTENER_METHOD))
           {
               if(((listener->flags & MESSAGE_BUS_LISTENER_METHOD) && (*l->cb_method == *listener->cb_method)) ||
                 ((!(listener->flags & MESSAGE_BUS_LISTENER_METHOD) && l->cb == listener->cb)))
               {
                   if ((listener->id == DEVICE_ID_ANY || listener->id == l->id) && (listener->value == DEVICE_EVT_ANY || listener->value == l->value))
                   {
                       // If notification of deletion has been requested, invoke the listener deletion callback.
                       if (listener_deletion_callback)
                           listener_deletion_callback(l);
   
                       // Found a match. mark this to be removed from the list.
                       l->flags |= MESSAGE_BUS_LISTENER_DELETING;
                       removed++;
                   }
               }
           }
   
           l = l->next;
       }
   
       if (removed > 0)
           return DEVICE_OK;
       else
           return DEVICE_INVALID_PARAMETER;
   }
   
   Listener* MessageBus::elementAt(int n)
   {
       Listener *l = listeners;
   
       while (n > 0)
       {
           if (l == NULL)
               return NULL;
   
           n--;
           l = l->next;
       }
   
       return l;
   }
   
   namespace codal {
   
   uint16_t allocateNotifyEvent()
   {
       return userNotifyId++;
   }
   
   }
   
   MessageBus::~MessageBus()
   {
       ignore(DEVICE_ID_SCHEDULER, DEVICE_EVT_ANY, this, &MessageBus::idle);
   }
