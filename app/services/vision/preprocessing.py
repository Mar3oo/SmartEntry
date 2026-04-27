import cv2
import numpy as np
from PIL import Image


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Improve image for OCR.

    Steps:
    - grayscale
    - threshold
    - denoise
    """

    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)

    return Image.fromarray(denoised)