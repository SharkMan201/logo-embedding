import pathlib
import os.path
from opencv_manager import embedWatermark, displayImage, writeImage

def getImagesPaths(startDir: str) -> list[str]:
    ret: list[str] = []
    for path in pathlib.Path(startDir).rglob('*'):
        if path.is_file() and (path.suffix == '.png' or path.suffix == '.jpg' or path.suffix == '.jpeg'):
            ret.append(path.as_posix())
    return ret

inputDir = 'input'
outputDir = 'output'
logoLightImagePath = 'assets/logo.png'
logoDarkImagePath = 'assets/logo-inverted.png'
offsetX = 50
offsetY = 50
opacity = 0.5
spacing = 500
logoScale = 0.5

def main():
    imagePaths = getImagesPaths(inputDir)

    totalImages = len(imagePaths)
    currentImageIdx = 0

    for img in imagePaths:
        currentImageIdx += 1
        printProgressBar(currentImageIdx, totalImages)
        outPath = outputDir + img.removeprefix(inputDir)

        # file already exisits no need to re-process it
        if os.path.isfile(outPath):
            print(outPath + " already exists.")
            continue

        img = embedWatermark(img, logoLightImagePath, spacing, offsetX, offsetY, opacity, logoScale)
        # displayImage(img)
        writeImage(img, outPath)
    
    print()

# Print iterations progress
def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

if __name__ == '__main__':
    main()