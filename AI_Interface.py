import time
import os
import numpy
import pygame, sys
import socket
import hashlib
import struct
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from threading import Thread

'''

Name: Brandon
Project Name: LAMBDA
File Description: Runs a python server that constantly listens for a client connection in "audioanalyze.py". OpenGL animates music file RMS from the client connection.
Last Date Modified: 7/13/2021

'''

x = None
data = 0
beginningHash = None

#Defines the dimensions of the shape
#Vertices and edges are correlated by index, first coordinate in vertices array = first node
def octahedron(x):
    y_stretch = x
    vertices = (
        (0, 1 + y_stretch, 0),
        (0, -1 - y_stretch, 0),
        (1, 0, 1),
        (1, 0, -1),
        (-1, 0, -1),
        (-1, 0, 1),
        )

    edges = (
        (0,2),
        (0,3),
        (0,4),
        (0,5),
        (1,2),
        (1,3),
        (1,4),
        (1,5),
        (3,4),
        (3,2),
        (5,2),
        (5,4)
        )


    surfaces = (
    (0,4,3), (0,2,3), (0,2,5), (0,5,4),
    (1,4,3), (1,2,3), (1,2,5), (1,5,4)
    )

    colors = (
    (1,0,0),
    (1,0,0),
    (0,0,1),
    (0,0,1),
    (0,1,0),
    (0,1,0),
    (1,0,1),
    (1,0,1)
    )

    glBegin(GL_TRIANGLES)
    for surface in surfaces:
        y = 0
        #(#,#,#) is for RGB values
        for vertex in surface:
            y += 1
            glColor3fv(colors[y])
            glVertex3fv(vertices[vertex])
    glEnd()

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

#Starts the pygame software and runs the GUI
def main():
    #Initialization
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)
    programIcon = pygame.image.load('atom.png')
    pygame.display.set_icon(programIcon)
    pygame.display.set_caption('L.A.M.B.D.A')
    gluPerspective(45, (display[0]/display[1]), 0.1, 50)
    glTranslatef(0.0,0.0, -5)
    #Main Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        glRotatef(1, 0, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #y_StretchFactor = numpy.sin(time.time() * 4)
        y_StretchFactor = data
        octahedron(y_StretchFactor)
        pygame.display.flip()
        pygame.time.wait(10)

#pick a large output buffer size because i dont necessarily know how big the incoming packet is\
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4)
s.bind((socket.gethostname(), 1241))
s.listen(5)

def serverListen():
    while True:
        print ("Listening for client . . .")
        clientsocket, address = s.accept()
        print ("Connected to client at ", address)
        while True:
            try:
                output = clientsocket.recv(4)
                output = struct.unpack('f', output)
                print(output[0])
                global data
                data = output[0]
                #data = (float(outputFinal) / 10000)
                #when client closes, the try fails and moves into except
            except:
                serverListen()

#Needs to be seperate from the initiate function, since the window needs to be open 24/7
if __name__ == "__main__":
    Thread(target = main).start()
    Thread(target = serverListen).start()
