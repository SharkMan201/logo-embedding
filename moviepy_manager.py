from moviepy import ImageClip, CompositeVideoClip, vfx
from pathlib import Path
import cv2
import os
import numpy as np
import math

logo_w = 400

class MoviePyManager():
    def __init__(self):
        return
    
    def getColorForLuminanceCalculation(self, color8Bit: int) -> float:
        colorSrgb = color8Bit / 255
        colorForLuminance: float

        if colorSrgb < 0.03928:
            colorForLuminance = colorSrgb / 12.92
        else:
            colorForLuminance = pow((colorSrgb + 0.055) / 1.055, 2.4)
        
        return colorForLuminance

    # https://www.w3.org/TR/WCAG20-TECHS/G17.html
    def getRelativeLuminanceForPixel(self, img: cv2.typing.MatLike, row: int, col: int) -> float:
        R = self.getColorForLuminanceCalculation(img[row, col][0])
        G = self.getColorForLuminanceCalculation(img[row, col][1])
        B = self.getColorForLuminanceCalculation(img[row, col][2])

        return 0.2126 * R + 0.7152 * G + 0.0722 * B



    def calculateTextClarityUsingLuminanceDiff(self, txtImg: cv2.typing.MatLike, backgroundImg: cv2.typing.MatLike) -> float:
        rows, cols, _ = txtImg.shape

        searchingForTheNextPixel = True
        contrasts: list[float] = []

        for i in range(rows):
            for j in range(cols):
                if txtImg[i, j][0] == 0 and txtImg[i, j][1] == 0 and txtImg[i, j][2] == 0:
                    # Just finished finding the first pixel
                    if not searchingForTheNextPixel:
                        searchingForTheNextPixel = True
                        # nothing before me
                        if j == 0:
                            continue

                        textLuminance = self.getRelativeLuminanceForPixel(txtImg, i, j - 1)
                        backgorundLuminance = self.getRelativeLuminanceForPixel(backgroundImg, i, j)
                        L = (max(textLuminance, backgorundLuminance) + 0.05) / (min(textLuminance, backgorundLuminance) + 0.05)
                        contrasts.append(L)
                # Just found the first pixel
                elif searchingForTheNextPixel:
                    searchingForTheNextPixel = False
                    # nothing before me
                    if j == 0:
                        continue
                    
                    textLuminance = self.getRelativeLuminanceForPixel(txtImg, i, j)
                    backgorundLuminance = self.getRelativeLuminanceForPixel(backgroundImg, i, j - 1)
                    L = (max(textLuminance, backgorundLuminance) + 0.05) / (min(textLuminance, backgorundLuminance) + 0.05)
                    contrasts.append(L)
        
        # return average contrasts
        return sum(contrasts) / len(contrasts)
    
    def getTextImgMeanIgnoringBlacks(self, textImg: cv2.typing.MatLike):
        rows, cols, _ = textImg.shape
        colorSum = [0, 0, 0]
        colorCount = 0

        for i in range(rows):
            for j in range(cols):
                if textImg[i, j][0] == 0 and textImg[i, j][1] == 0 and textImg[i, j][2] == 0:
                    continue
                colorSum += textImg[i, j]
                colorCount += 1
        
        return [x / colorCount for x in colorSum]
    
    # https://answers.opencv.org/question/217850/contrast-detection-picking-the-right-font-color/
    def calculateTextClarityUsingmeans(self, txtImg: cv2.typing.MatLike, backgroundImg: cv2.typing.MatLike) -> float:
        color_mean = np.mean(backgroundImg, axis=(0, 1))
        img_r = color_mean[0]
        img_g = color_mean[1]
        img_b = color_mean[2]

        # text_mean = np.mean(txtImg, axis=(0, 1))
        text_mean = self.getTextImgMeanIgnoringBlacks(txtImg)
        text_r = text_mean[0]
        text_g = text_mean[1]
        text_b = text_mean[2]

        dist = math.sqrt(pow(img_r - text_r, 2) + pow(img_g - text_g, 2) + pow(img_b - text_b, 2))
        return dist
    
    # 0 -> light top left
    # 1 -> light top right
    # 2 -> light bottom left
    # 3 -> light bottom right
    # 4 -> dark top left
    # 5 -> dark top right
    # 6 -> dark bottom left
    # 7 -> dark bottom right
    def getBestLogoPlacement(self, inpLogoLight: ImageClip, inpLogoDark: ImageClip, inpImg: ImageClip, inpImagePath: str, outPath: str) -> int:
        logoImg0: ImageClip = inpLogoLight.with_position(("left", "top"))
        logoImg1: ImageClip = inpLogoLight.with_position(("right", "top"))
        logoImg2: ImageClip = inpLogoLight.with_position(("left", "bottom"))
        logoImg3: ImageClip = inpLogoLight.with_position(("right", "bottom"))
        
        logoImg4: ImageClip = inpLogoDark.with_position(("left", "top"))
        logoImg5: ImageClip = inpLogoDark.with_position(("right", "top"))
        logoImg6: ImageClip = inpLogoDark.with_position(("left", "bottom"))
        logoImg7: ImageClip = inpLogoDark.with_position(("right", "bottom"))

        logoImagesLight = [logoImg0, logoImg1, logoImg2, logoImg3]
        logoImagesDark = [logoImg4, logoImg5, logoImg6, logoImg7]

        # Create dirs if not exists
        Path(outPath).parent.mkdir(exist_ok=True, parents=True)

        editedImg: ImageClip = CompositeVideoClip([inpImg] + logoImagesLight, (inpImg.w, inpImg.h)).to_ImageClip()
        editedImg.save_frame(outPath + '-light.png', with_mask=False)
        inpLogoLight.save_frame(outPath + '-logo-light.png', with_mask=False)

        editedImg: ImageClip = CompositeVideoClip([inpImg] + logoImagesDark, (inpImg.w, inpImg.h)).to_ImageClip()
        editedImg.save_frame(outPath + '-dark.png', with_mask=False)
        inpLogoDark.save_frame(outPath + '-logo-dark.png', with_mask=False)

        ret = 0
        maxClarity = 0

        imgLight = cv2.imread(outPath + '-light.png', cv2.IMREAD_COLOR_RGB)
        imgDark = cv2.imread(outPath + '-dark.png', cv2.IMREAD_COLOR_RGB)

        logoImgLight = cv2.imread(outPath + '-logo-light.png', cv2.IMREAD_COLOR_RGB)
        logoImgDark = cv2.imread(outPath + '-logo-dark.png', cv2.IMREAD_COLOR_RGB)

        croppedLogos = [
            imgLight[0:inpLogoLight.h, 0:inpLogoLight.w],
            imgLight[0:inpLogoLight.h, -1 * inpLogoLight.w:],
            imgLight[-1 * inpLogoLight.h:, 0:inpLogoLight.w],
            imgLight[-1 * inpLogoLight.h:, -1 * inpLogoLight.w:],
            imgDark[0:inpLogoLight.h, 0:inpLogoLight.w],
            imgDark[0:inpLogoLight.h, -1 * inpLogoLight.w:],
            imgDark[-1 * inpLogoLight.h:, 0:inpLogoLight.w],
            imgDark[-1 * inpLogoLight.h:, -1 * inpLogoLight.w:]
        ]

        impImgCv = cv2.imread(inpImagePath, cv2.IMREAD_COLOR_RGB)

        croppedOriginalImg = [
            impImgCv[0:inpLogoLight.h, 0:inpLogoLight.w],
            impImgCv[0:inpLogoLight.h, -1 * inpLogoLight.w:],
            impImgCv[-1 * inpLogoLight.h:, 0:inpLogoLight.w],
            impImgCv[-1 * inpLogoLight.h:, -1 * inpLogoLight.w:]
        ]

        for i in range(0, 8):
            # cv2.imshow('Test', croppedLogos[i])
            # cv2.waitKey(0)
            # clarity = self.calculateTextClarityUsingLuminanceDiff(logoImgLight if i < 4 else logoImgDark, croppedOriginalImg[i % 4])
            clarity = self.calculateTextClarityUsingmeans(logoImgLight if i < 4 else logoImgDark, croppedOriginalImg[i % 4])
            print(clarity)
            if clarity > maxClarity:
                maxClarity = clarity
                ret = i
        
        os.remove(outPath + '-light.png')
        os.remove(outPath + '-dark.png')
        os.remove(outPath + '-logo-light.png')
        os.remove(outPath + '-logo-dark.png')

        return ret

    
    def EmbedLogo(self, inpLogoLightPath: str, inpLogoDarkPath: str, inpImgPath: str, outPath: str):
        logoImgLight = ImageClip(inpLogoLightPath)
        logoImgDark = ImageClip(inpLogoDarkPath)
        inpImg = ImageClip(inpImgPath)

        scale = logo_w / logoImgLight.w

        logoImgLight: ImageClip = logoImgLight.with_effects([vfx.Resize(scale)])
        logoImgDark: ImageClip = logoImgDark.with_effects([vfx.Resize(scale)])

        bestPlacement = self.getBestLogoPlacement(logoImgLight, logoImgDark, inpImg, inpImgPath, outPath)

        logoImg: ImageClip
        if bestPlacement < 4:
            logoImg: ImageClip = logoImgLight.with_position(('right' if bestPlacement & 1 > 0 else 'left', 'bottom' if bestPlacement & 2 > 0 else 'top'))
        else:
            logoImg: ImageClip = logoImgDark.with_position(('right' if bestPlacement & 1 > 0 else 'left', 'bottom' if bestPlacement & 2 > 0 else 'top'))

        editedImg: ImageClip = CompositeVideoClip([inpImg, logoImg], (inpImg.w, inpImg.h)).to_ImageClip()
        
        # Create dirs if not exists
        Path(outPath).parent.mkdir(exist_ok=True, parents=True)
        editedImg.save_frame(outPath, with_mask=False)

