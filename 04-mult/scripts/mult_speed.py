#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Basic imports.  Not all may be required.
from pynq import Overlay
from pynq import allocate
from pynq.ps import Clocks
import numpy as np


# In[ ]:


# Load the overlay to the design
overlay = Overlay('speed_test.bit')


# In[ ]:


def send_data(overlay, values):
    N = len(values)  # Number of words - should be multiple of 2
    r = overlay.axi_fifo_mm_s_0.register_map
    r.ISR = 0xFFFFFFFF  # Clear all interrupts
    r.IER=0x0C000000    # Enable TX and RX complete interrupts
    r.TDR=0             # Destination - not used
    for i in values:    # Send the data
        r.TDFD = i
    r.TLR = N * 4       # Set length for transmission
    


# In[ ]:


def recv_data(overlay):
    # Assumes send has already been done
    r = overlay.axi_fifo_mm_s_0.register_map
    rx = r.RDFO
#     print(f"{rx} values remaining to be read")
    values = []
    for i in range(rx):
        values.append(r.RDFD.Read_Data_Value)
    return values


# In[ ]:


def check_errors(out, expout):
    count = 0
    for (x, y) in zip(out, expout):
        if x != y:
            print(f"exp: {y} ({y:08x}): error: {x^y:08x}")
            count += 1
    print(f"{count} out of {len(out)} errors")
    return count


# In[ ]:


from random import randint
N=16
inputs = []
expout = []
for i in range(N):
    a = randint(-2**31, 2**31-1)
    b = randint(-2**31, 2**31-1)
    c = (a * b) & 0xFFFFFFFF
    inputs.append(a)
    inputs.append(b)
    expout.append(c)
m = 0xFFFFFFFF
inputs.append(m)
inputs.append(m)
expout.append((m*m) & m)
# print(inputs)
# print(expout)


# In[ ]:


# Set up clocks
print(f"CPU Clock frequency = {Clocks.cpu_mhz} MHz")
Clocks.fclk0_mhz=100
Clocks.fclk1_mhz=100
print(f"Set AXI clock to {Clocks.fclk0_mhz} MHz, PL clock to {Clocks.fclk1_mhz} MHz")


# In[ ]:


send_data(overlay, inputs)


# In[ ]:


rx = recv_data(overlay)


# In[ ]:


numerrors = check_errors(rx, expout)


# In[ ]:




