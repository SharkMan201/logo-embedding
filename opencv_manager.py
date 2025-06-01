import cv2
import numpy as np
from pathlib import Path
import os

def readImage(imgPath: str) -> cv2.typing.MatLike:
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    return cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

def writeImage(img: cv2.typing.MatLike, outPath: str):
    dir = os.path.dirname(outPath) 
    Path(dir).mkdir(parents=True, exist_ok=True)
    cv2.imwrite(outPath, img)

def displayImage(img: cv2.typing.MatLike):
    cv2.imshow('img', img)
    cv2.waitKey(0)

def scaleImage(img: cv2.typing.MatLike, scale: float) -> cv2.typing.MatLike:
    h, w, _ = img.shape
    h = int(h * scale)
    w = int(w * scale)
    ret = cv2.resize(img, dsize=(w, h), interpolation=cv2.INTER_LINEAR)
    return ret

def padImage(img: cv2.typing.MatLike, pL: int, pR: int, pT: int, pB: int) -> cv2.typing.MatLike:
    h, w, c = img.shape
    w = w + pL + pR
    h = h + pT + pB

    retImg = np.zeros((h, w, c), np.uint8)
    retImg[pT: h - pB, pL: w - pL] = img
    return retImg

def cropImage(img: cv2.typing.MatLike, x1: int, y1: int, x2: int, y2: int) -> cv2.typing.MatLike:
    return img[y1: y2, x1: x2]

def overlayImages(backgroundImage: cv2.typing.MatLike, foregroundImage: cv2.typing.MatLike, x: int, y: int, opacity: float) -> cv2.typing.MatLike:
    foregroundImageHeight, foregroundImageWidth, _ = foregroundImage.shape
    outImg = backgroundImage.copy()
    roi = outImg[y: y + foregroundImageHeight, x: x + foregroundImageWidth]

    # normalize alpha channels from 0-255 to 0-1
    alpha_background = roi[:,:,3] / 255.0
    alpha_foreground = (foregroundImage[:,:,3] * opacity) / 255.0

    for color in range(0, 3):
        roi[:,:,color] = alpha_foreground * foregroundImage[:,:,color] + alpha_background * roi[:,:,color] * (1 - alpha_foreground)
    
    roi[:,:,3] = (1 - (1-alpha_foreground) * (1 - alpha_background)) * 255
    outImg[y: y + foregroundImageHeight, x: x + foregroundImageWidth] = roi
    return outImg
    

def embedWatermark(imgPath: str, logoPath: str, spacing: float, offsetX: int, offsetY: int, opacity: float, logoScale: float) -> cv2.typing.MatLike:
    img = readImage(imgPath)
    logo = readImage(logoPath)

    logo = scaleImage(logo, logoScale)
    logoHeight, logoWidth, _ = logo.shape

    img = padImage(img, logoWidth, logoWidth, logoHeight, logoHeight)
    imgHeight, imgWidth, _ = img.shape

    i = 0
    for x in range(offsetX, imgWidth - logoWidth, int(spacing * logoWidth)):
        i += 1
        j = 0
        for y in range(offsetY, imgHeight - logoHeight, int(spacing * logoHeight)):
            j += 1
            if (i + j) % 2 != 1:
                continue
            img = overlayImages(img, logo, x, y, opacity)
    
    return cropImage(img, logoWidth, logoHeight, imgWidth - logoWidth, imgHeight - logoHeight)
