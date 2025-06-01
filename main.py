import glob
import pathlib
from moviepy_manager import MoviePyManager
import os.path

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

def main():
    imagePaths = getImagesPaths(inputDir)
    moviepyManager: MoviePyManager = MoviePyManager()

    for img in imagePaths:
        outPath = outputDir + img.removeprefix(inputDir)

        # file already exisits no need to re-process it
        if os.path.isfile(outPath):
            print(outPath + " already exists.")
            continue

        moviepyManager.EmbedLogo(logoLightImagePath, logoDarkImagePath, img, outPath)

        # break

if __name__ == '__main__':
    main()