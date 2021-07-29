import time
import os
import sys
import numpy
import socket
import struct
import wave
import librosa
import soundfile as sf
from threading import Thread
import pygame
from multiprocessing import Process,Pipe

'''

Name: Brandon
Project Name: LAMBDA
File Description: Analyzes a music file using root mean square and feeds each iteration of data through a client connection to audiovisual. It also plays the music file in sync with the RMS data feed.
Last Date Modified: 7/13/2021

'''

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 1241))
except:
    sys.exit()

audioBuffer, sr = librosa.load('speech.wav')
f = sf.SoundFile('speech.wav')
#print('samples = {}'.format(len(f)))
#print('sample rate = {}'.format(f.samplerate))
#print('seconds = {}'.format(len(f) / f.samplerate))

RMS = 0
status = False
audiotime_elapsed = 0
audiotime_array = []
currentSampleList = []
timeSoundBegan = 0
globalvariable = 0

def speech():
    global timeSoundBegan
    timeSoundBegan = time.time()
    playSound('speech.wav')
    #time.sleep((len(f) / f.samplerate))

def playSound(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    #time.sleep(len(f) / f.samplerate)
    status = True
    sys.exit()

def main():
    while (status == False):
        #time.sleep(1)
        #global audiotime_elapsed
        #audiotime_elapsed = audiotime_elapsed + 1
        #to find currentSample = ((audiotime_elapsed) * samplerate
        audiotime_elapsed = time.time() - timeSoundBegan
        indexOfCurrentSample = ((audiotime_elapsed) * sr)
        bufferSize = 0.1 * sr
        result = 0
        if (indexOfCurrentSample < len(audioBuffer)):
            for index in range (int(indexOfCurrentSample - bufferSize), int(indexOfCurrentSample)):
                #print(index)
                if (index > 0):
                    result += (audioBuffer[index] ** 2)
                    #print(result)
                else:
                    None
                #print(indexOfCurrentSample)
                    #handle when indexOfCurrentSample is less than bufferSize (early in the program's life) so that index is never negative
                    #multiply audioBuffer[index] by itself
                    #add it to sum
                    #print(result)
        else:
            return
        total = (result/bufferSize)
        global RMS
        RMS = numpy.sqrt(total) * 15
        RMS = struct.pack('f', RMS)
        #data = str(globalvariable)
        s.send(RMS)

if __name__ == "__main__":
    Thread(target = speech).start()
    Thread(target = main).start()
