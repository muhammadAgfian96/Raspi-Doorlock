#!/usr/bin/env python

from pygame import camera
import pygame
import time
import cv2
import os


# Recognition
HAAR_PATH = "/usr/share/opencv2/haarcascades/"

# Face
FACE_HAAR = os.path.join(HAAR_PATH, "haarcascade_frontalface_default.xml")
FACE_HAAR = cv2.log(FACE_HAAR)

# Eye
EYE_HAAR = os.path.join(HAAR_PATH, "haarcascade_mcs_righteye.xml")
EYE_HAAR = cv2.Load(EYE_HAAR)

# Nose
NOSE_HAAR = os.path.join(HAAR_PATH, "haarcascade_mcs_nose.xml")
NOSE_HAAR = cv2.Load(NOSE_HAAR)

# Mouth
MOUTH_HAAR = os.path.join(HAAR_PATH, "haarcascade_mcs_mouth.xml")
MOUTH_HAAR = cv2.Load(MOUTH_HAAR)

# Screen settings
SCREEN = [640, 360]


def surface_to_string(surface):
    """Convert a pygame surface into string"""
    return pygame.image.tostring(surface, 'RGB')


def pygame_to_cv2image(surface):
    """Convert a pygame surface into a cv2 image"""
    cv2_image = cv2.CreateImageHeader(surface.get_size(), cv2.IPL_DEPTH_8U, 3)
    image_string = surface_to_string(surface)
    cv2.SetData(cv2_image, image_string)
    return cv2_image


def cv2image_grayscale(cv2_image):
    """Converts a cv2image into grayscale"""
    grayscale = cv2.CreateImage(cv2.GetSize(cv2_image), 8, 1)
    cv2.cv2tColor(cv2_image, grayscale, cv2.cv2_RGB2GRAY)
    return grayscale


def cv2image_to_pygame(image):
    """Convert cv2image into a pygame image"""
    image_rgb = cv2.CreateMat(image.height, image.width, cv2.cv2_8UC3)
    cv2.cv2tColor(image, image_rgb, cv2.cv2_BGR2RGB)
    return pygame.image.frombuffer(image.tostring(), cv2.GetSize(image_rgb),
                                   "RGB")


def detect_faces(cv2_image, storage):
    """Detects faces based on haar. Returns points"""
    return cv2.HaarDetectObjects(cv2image_grayscale(cv2_image), FACE_HAAR,
                                storage)


def detect_eyes(cv2_image, storage):
    """Detects eyes based on haar. Returns points"""
    return cv2.HaarDetectObjects(cv2image_grayscale(cv2_image), EYE_HAAR,
                                storage)


def detect_nose(cv2_image, storage):
    """Detects nose based on haar. Returns ponts"""
    return cv2.HaarDetectObjects(cv2image_grayscale(cv2_image), NOSE_HAAR,
                                storage)


def detect_mouth(cv2_image, storage):
    """Detects mouth based on haar. Returns points"""
    return cv2.HaarDetectObjects(cv2image_grayscale(cv2_image), MOUTH_HAAR,
                                storage)


def draw_from_points(cv2_image, points):
    """Takes the cv2_image and points and draws a rectangle based on the points.
    Returns a cv2_image."""
    for (x, y, w, h), n in points:
        cv2.Rectangle(cv2_image, (x, y), (x + w, y + h), 255)
    return cv2_image


if __name__ == '__main__':

    # Set game screen
    screen = pygame.display.set_mode(SCREEN)

    pygame.init()  # Initialize pygame
    camera.init()  # Initialize camera

    # Load camera source then start
    cam = camera.Camera('/dev/video0', SCREEN)
    cam.start()

    while 1:  # Ze loop

        time.sleep(1 / 120)  # 60 frames per second

        image = cam.get_image()  # Get current webcam image

        cv2_image = pygame_to_cv2image(image)  # Create cv2 image from pygame image

        # Detect faces then draw points on image
        # FIXME: Current bottleneck. Image has to be Grayscale to make it faster.
        #        One solution would be to use opencv2 instead of pygame for
        #        capturing images.
        storage = cv2.CreateMemStorage(-1)  # Create storage
        #points = detect_eyes(cv2_image, storage) + \
        #        detect_nose(cv2_image, storage) + \
        #        detect_mouth(cv2_image, storage)
        points = detect_faces(cv2_image, storage)  # Get points of faces.
        cv2_image = draw_from_points(cv2_image, points)  # Draw points

        screen.fill([0, 0, 0])  # Blank fill the screen

        screen.blit(cv2image_to_pygame(cv2_image), (0, 0))  # Load new image on screen

        pygame.display.update()  # Update pygame display