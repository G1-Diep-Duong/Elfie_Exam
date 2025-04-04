import pyautogui
from PIL.Image import Image

from . import logger


def get_box(img: Image, full_img: Image, scale: int = 100, confidence: int = 99):
    try:
        with img.resize((int(img.size[0] * scale / 100), int(img.size[1] * scale / 100))) as baseline_image:
            return pyautogui.locate(baseline_image, full_img, confidence=(confidence / 100))
    except Exception as exception:
        logger.error(exception)
        return None
