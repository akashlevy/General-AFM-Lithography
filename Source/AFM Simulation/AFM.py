#Tilt the tip, be able to turn image on or off.

#Included modules
from __future__ import division
from visual.controls import *
from PIL import Image
import math
import os

#Define constants
default_width = 800
default_height = 600
default_forward = vector(0.597258, -0.712878, 0.367541)
speed = 30
step_size = .1

raised_height = 2

#Initialize useful variables
image_height = 30
image_width = 30
x_offset = 0
y_offset = 0

#Window settings
scene.title = 'AFM Visualization'
scene.background = color.white
scene.foreground = color.black
scene.width=default_width
scene.height=default_height
scene.forward=default_forward
scene.autoscale = False
scene.lights = [distant_light(direction=(0.22, 0.44, 0.88), color=color.gray(0.8)), distant_light(direction=(-0.88, -0.22, -0.44), color=color.gray(0.3)), distant_light(direction=(0, 1, 0), color=color.gray(0.3))]

#Define trace-line and add-point function
all_lines = []
def addpoint(x,y):
    all_lines[len(all_lines)-1].append(pos = (-y,0,x))

#Define surface
surface = box(color = color.yellow, size = (70, 1.5, 70))
surface.y = -surface.height/2

#Read initial settings
try:
    read_stream = open('C:\\AFM\\settings.ini', 'r')
except Exception:
    pass
try:
    image_height = float(read_stream.readline())
except Exception:
    pass
try:
    image_width = float(read_stream.readline())
except Exception:
    pass
try:
    x_offset = float(read_stream.readline())
except Exception:
    pass
try:
    y_offset = float(read_stream.readline())
except Exception:
    pass
try:
    read_stream.close()
except Exception:
    pass

#Define image projected on surface
try:
    im = Image.open('C:\\AFM\\surfacepic.jpg')
except Exception:
    pass
try:
    im = Image.open('C:\\AFM\\surfacepic.jpeg')
except Exception:
    pass
im = im.resize((512,512), Image.ANTIALIAS)
texture = materials.texture(data=im, mapping='sign')
projected_image = box(axis = (0,1,0), length = .005, width = image_width, height = image_height, material=texture)

#Define AFM tip components
AFM = frame()
point = cone(frame = AFM, y = raised_height, axis=(0,-2,0), radius = 1, color = color.cyan)
color_rgb = (242/255,170/255,200/255)
handle = box(frame = AFM, color = color_rgb, pos = (0,point.y,point.z), length = 15, height = .75, width = 2.5*point.radius)
handle_original_x = handle.length/2 - 1.25*point.radius
handle.x = handle_original_x

#Define movement and interpretation functions (x is away along side of afm box, y is along side of surface)
def jumptopos(x,y,trace):
    x+=x_offset
    y+=y_offset
    handle.z = x
    point.z = x
    point.x = -y
    handle.x = -y + handle_original_x
    if trace:
        addpoint(x,y)        
    
def movetopos(x,y):
    begin_x = -point.z
    begin_y = -point.x
    distance = sqrt((y-begin_y)**2 + (x-begin_x)**2)
    if (x - begin_x) != 0:
        angle = atan2(y-begin_y,x-begin_x)
    elif (y-begin_y) > 0:
        angle = pi/2
    else:
        angle = -pi/2
    for i in range(int(distance/step_size)):
        jumptopos(begin_x+i*step_size*cos(angle), begin_y+i*step_size*sin(angle))
        rate(speed)
    jumptopos(x,y)

def draw(voltage):
    if voltage > 3:
        return 1
    if voltage < -3:
        return 1
    else:
        return 0

#Define variables before loop
color = color.black
line_width = 0.01
x = 0
y = 0
voltage = 0
oldx = 0.
oldy = 0.
oldcolor = (0,0,0)
oldvoltage = 0.
oldline_width = 0.
oldcenter = (0,0,0)
oldvisible = True
first = True

#Reset file before loop
write_stream = open('C:\\AFM\\00.tmp', 'w')
write_stream.write("0\n0\n0\n(0,0,0)\n(0,0,0)\n1\n10")
write_stream.close()

#Actions
while True:
    #Adjust rate of program
    rate(speed)

    #Read data from command.tmp
    fail = False
    try:
        command_stream = open('C:\\AFM\\command.tmp', 'r')
    except Exception:
        fail = True
    if not fail:
        try:
            exec(command_stream.read())
        except Exception:
            fail = True
        command_stream.close()
        try:
            os.remove('C:\\AFM\\command.tmp')
        except Exception:
            pass

    #Read data from data stream (if ready) and interpret
    read_stream = open('C:\\AFM\\00.tmp', 'r')
    try:
        x = float(read_stream.readline())
    except ValueError:
        pass
    try:
        y = float(read_stream.readline())
    except ValueError:
        pass
    try:
        exec("color = " + read_stream.readline())
    except Exception:
        color = oldcolor
    try:
        line_width = float(read_stream.readline())
    except ValueError:
        pass
    try:
        exec("scene.center = " + read_stream.readline())
    except Exception:
        pass
    try:
        AFM.visible = int(read_stream.readline())
    except ValueError:
        AFM.visible = oldvisible
    try:
        voltage = float(read_stream.readline())
    except ValueError:
        pass
        
    if (x != oldx) or (y != oldy) or (color != oldcolor) or (line_width != oldline_width):
        if (color != oldcolor) or (line_width != oldline_width) or (len(all_lines[len(all_lines)-1].pos) >= 950):
            all_lines.append(curve(radius = line_width))
            try:
                all_lines[len(all_lines)-1].color = color
                point.color = color
            except Exception:
                pass
        jumptopos(x,y, draw(voltage) * (not first))
        oldx = x
        oldy = y
        oldcolor = color
        oldline_width = line_width
        oldvoltage = voltage
    if first:
        first = False
    read_stream.close()
