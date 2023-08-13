
import board
import displayio
import adafruit_imageload
import vectorio
import time
import random
import neopixel
import framebufferio
import rgbmatrix
import math
import rainbowio
# Turn off onboard NeoPixel
pix = neopixel.NeoPixel(board.NEOPIXEL,1)
pix.fill(0)
# Release and initialize display
displayio.release_displays()
MATRIX = rgbmatrix.RGBMatrix(
    width=64, bit_depth=6,#bit_depth = 4
    rgb_pins=[board.D6, board.A5, board.A1, board.A0, board.A4, board.D11],
    addr_pins=[board.D10, board.D5, board.D13, board.D9],
    clock_pin=board.D12, latch_pin=board.RX, output_enable_pin=board.TX)
display = framebufferio.FramebufferDisplay(MATRIX,auto_refresh = True)

def mirror(x):
    '''
    mirrors the x position of a point across the center
    '''
    return ((32 - x)*2) + x

def sin_displace(ypos_init,phase,depth):
    '''
    ypos_init: initial y position
    phase: shifts the sin wave in or out of phase
    depth: how many pixels to move
    TODO: add freq which is the '3' in the math.sin arg below
    TODO: add incrementor(?) to replace time.monotonic() to make it not dependent on time
    '''
    sin = math.sin((time.monotonic()*3) + phase) + 1
    return int((sin/2)*depth) + ypos_init
# Create a Group to hold the TileGrid
group = displayio.Group()
# Make a palette of one color
palette = displayio.Palette(1)
# Assign that palette a color
palette[0] = [200,50,170]

# Below we create two polygons with points and a starting position
# If starting position equals x=0, y=0 then the points of the polygons
# directly correspond to the position on the display
# otherwise it is relative to the x and y initialized here (which can be changed!)
points=[(7,5), (26,25),(3,23)]
polygon = vectorio.Polygon(pixel_shader=palette, points=points, x=0, y=0)
mirpoly_points = [(mirror(7),5), (mirror(26),25),(mirror(3),23)]
mirpoly = vectorio.Polygon(pixel_shader=palette, points=mirpoly_points, x=0, y=0)

# Append our polygons to the group
group.append(polygon)
group.append(mirpoly)

# Show our group
display.show(group)

# Initialize some variables
last_time = time.monotonic()
last_time_print = time.monotonic()
time_between_moves = 0.008
frame_times = []
while True:
    #get current time for loop timing
    start = time.monotonic_ns()
    #assign palette (color of all elements) a color based on the time for a rainbow effect
    palette[0] = rainbowio.colorwheel(time.monotonic_ns()//2e7)

    #get current time (again)
    now = time.monotonic()

    #non blocking timer will space out updates to polygon position
    #we dont need to do all this math all the time!
    #it doesnt move that much and doing this math is wasteful if it calculates
    #that its in the same spot
    if now - last_time   > time_between_moves:
        vertex_1 = sin_displace(4,0,9)#(y pos intial, phase, depth)
        vertex_2 = sin_displace(21,3,9)
        vertex_3 = sin_displace(19,2,9)
        polygon.points = [(7,vertex_1), (26,vertex_2),(3,vertex_3)]
        mirpoly.points = [(mirror(7),vertex_1), (mirror(26),vertex_2),(mirror(3),vertex_3)]
        last_time = now

    # End timer for loop timing
    end = time.monotonic_ns()

    # appends the time it takes from top to bottom
    frame_times.append((end-start)//1e6)
    #might not be 'frametime' exactly. more like loop time
    if now - last_time_print > 1:
        avg_frametime = sum(frame_times)/len(frame_times)
        framerate = 1/(avg_frametime /1000)
        print(f'Average frametime: {avg_frametime:.2f}ms FPS: {framerate:.0f}',end = '\r')
        frame_times = []
        last_time_print = now

