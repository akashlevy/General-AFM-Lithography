#Included modules
from __future__ import division
from visual.controls import *
from PIL import Image
import math, os

#Define constants
defaultSceneWidth = 800
defaultSceneHeight = 600
defaultSceneForward = vector(0.9,-0.5,0)
speed = 30
stepSize = 0.1
raisedHeight = 2

#Initialize useful variables
imageHeight = 40
imageWidth = 40

#Window settings
scene.title = "AFM Visualization"
scene.background = color.white
scene.foreground = color.black
scene.width = defaultSceneWidth
scene.height = defaultSceneHeight
scene.forward = defaultSceneForward
scene.lights = [distant_light(direction=(0.22,0.44,0.88), color=color.gray(0.8)), distant_light(direction=(-0.88,-0.22,-0.44), color=color.gray(0.3)), distant_light(direction=(0,1,0), color=color.gray(0.3))]

#Paths to resources
settingsPath = "C:\\AFM\\settings.ini"
comPath = "C:\\AFM\\00.tmp"
imagePath = "C:\\AFM\\surfacepic.jpg"

#Define trace-line and add-point function
allLines = []
def addPoint(x,y):
    allLines[-1].append(pos = (-y,0,x))

#Read image settings
try:
    readStream = open(settingsPath, "r")
    projected.height = float(readStream.readline())
    projected.width = float(readStream.readline())
    readStream.close()
except Exception:
    pass

#Define image projected on surface
try:
    image = Image.open(imagePath)
except Exception:
    pass
try:
    image = Image.open(imagePath)
except Exception:
    pass
try:
    image = image.resize((512,512), Image.ANTIALIAS)
    image = image.rotate(90, expand=0)
    texture = materials.texture(data=image, mapping="sign")
    projectedImage = box(axis=(0,1,0), length=0.005, width=imageWidth, height=imageHeight, material=texture)
except Exception:
    pass

#Define surface
surface = box(color=color.gray(0.4), size=(imageWidth, 1.5, imageHeight))
surface.y = -surface.height/2

#Define AFM tip components
AFM = frame()
point = cone(frame=AFM, y=raisedHeight, axis=(0, -2, 0), radius=1, color=color.black)
handleShape = Polygon([(1.25*point.radius, 1.25*point.radius), (5*point.radius, -12.5), (2.5*point.radius, -12.5), (0,-1.25), (-2.5*point.radius, -12.5), (-5*point.radius, -12.5), (-1.25*point.radius, 1.25*point.radius)])
handle = extrusion(frame=AFM, shape=handleShape, pos=[(0, raisedHeight+0.25, 0),(0, raisedHeight-0.5, 0)], color=color.gray(0.6))

#Define movement and interpretation functions
def jumpToPos(x, y, trace):
    AFM.z = x
    AFM.x = -y
    if trace:
        addPoint(x,y)

def draw(voltage):
    if voltage > 3:
        return 1
    if voltage < -3:
        return 1
    else:
        return 0

#Define variables before loop
color = color.black
lineWidth = 0.01
x = 0
y = 0
voltage = 0
oldX = 0.0
oldY = 0.0
oldColor = (0,0,0)
oldVoltage = 0.0
oldLineWidth = 0.0
oldCenter = (0,0,0)
oldVisible = True
first = True

#Reset file before loop
writeStream = open(comPath, "w")
writeStream.write("0\n0\n0\n(0,0,0)\n(0,0,0)\n1\n0")
writeStream.close()

#Actions
while True:
    #Adjust rate of program
    rate(speed)

    #Read data from data stream (if ready) and interpret
    readStream = open(comPath, "r")
    try:
        x = float(readStream.readline())
        y = float(readStream.readline())
        color =  eval(readStream.readline())
        lineWidth = float(readStream.readline())
        scene.center = eval(readStream.readline())
        AFM.visible = int(readStream.readline())
        voltage = float(readStream.readline())
    except Exception:
        pass

    #Add point    
    if (x != oldX) or (y != oldY) or (color != oldColor) or (lineWidth != oldLineWidth):
        if (color != oldColor) or (lineWidth != oldLineWidth) or (len(allLines[-1].pos) >= 950):
            allLines.append(curve(radius=lineWidth))
            try:
                allLines[-1].color = color
                point.color = color
            except Exception:
                pass
        jumpToPos(x, y, draw(voltage)*(not first))
        oldX = x
        oldY = y
        oldColor = color
        oldLineWidth = lineWidth
        oldVoltage = voltage
    if first:
        first = False
    readStream.close()
