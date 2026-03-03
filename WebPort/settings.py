import pygame

#Scaling values
NATIVE_WIDTH  = 1920
NATIVE_HEIGHT = 1080
WIDTH  = 1280
HEIGHT = 720
WINDOW_SIZE=(1280,720) #New window size

SCALE  = WIDTH / NATIVE_WIDTH  #Scale factor

def S(value): #Scaling single value
    return int(value * SCALE)

def SP(x, y): #Scaling x,y values
    return (int(x * SCALE), int(y * SCALE))

#Colors ( inconsisten with the usage, I know , should have added all the colors i use and actually call it beacause its mostly WHITE called)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#Bounds
top_bound = 100 #566 #333
bottom_bound = 800
top_bound2 = 200 
bottom_bound2 = 950 

FPS=60