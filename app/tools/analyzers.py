from pdf2image import convert_from_bytes
import wcag_contrast_ratio as contrast

import cv2
import numpy as np
import pytesseract
from pytesseract import Output

from sklearn.cluster import KMeans


def get_dominant_colors(image, clusters):
    image = image.reshape((image.shape[0] * image.shape[1], 3))
    k_means = KMeans(n_clusters=clusters)
    k_means.fit(image)

    json_serializable = [list(map(int, row)) for row in list(map(list, k_means.cluster_centers_.astype(int)))]

    return json_serializable


def normalize_rgb(color):
    return [color[0]/255, color[1]/255, color[2]/255]


class Document:
    max_slides = 30

    def __init__(self, file: bytes, language: str = "eng"):
        images = convert_from_bytes(file)
        self.images = list(map(np.array, images))
        self.language = language

    def __extract_image_data__(self, image):
        image_to_ocr = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_data = pytesseract.image_to_data(
            image_to_ocr,
            lang=self.language,
            output_type=Output.DICT
        )

        return image_data

    def __extract_text_boxes__(self, image):
        image_data = self.__extract_image_data__(image)

        for i in range(0, len(image_data['text'])):
            x = image_data["left"][i]
            y = image_data["top"][i]
            w = image_data["width"][i]
            h = image_data["height"][i]

            text = image_data["text"][i]
            confidence = int(image_data["conf"][i])

            are_letters = any([e.isalpha() for e in "".join(text.split())])
            if confidence > 75 and are_letters:
                text_box = image[y: y + h, x: x + w]

                yield text_box, text

    def wcag_compliance(self):

        overall_compliance = {
            "total": 0,
            "slides": []
        }

        for image in self.images:
            text_data = self.__extract_text_boxes__(image)
            slide = {"wcag_compliance": 0, "text": []}

            for text_datum in text_data:
                text_box, text = text_datum

                colors = get_dominant_colors(text_box, 2)
                ratio = contrast.rgb(normalize_rgb(colors[0]), normalize_rgb(colors[1]))
                wcag_compliance = contrast.passes_AA(ratio)

                slide.get("text").append({
                    "text": text, "colors": colors, "ratio": ratio, "wcag_compliance": wcag_compliance
                })

                if len(slide["text"]):
                    slide_wcag_compliance = [text["wcag_compliance"] for text in slide.get("text")].count(True)
                    slide["wcag_compliance"] = round(slide_wcag_compliance/len(slide["text"]), 2)

            overall_compliance["slides"].append(slide)

        if len(overall_compliance["slides"]):
            wcag_compliant = sum([slide["wcag_compliance"] for slide in overall_compliance.get("slides")])
            overall_compliance["total"] = round(wcag_compliant/len(overall_compliance["slides"]), 2)

        return overall_compliance

    def volume(self):
        number_of_slides = len(self.images)
        return {"volume_compliance": number_of_slides <= self.max_slides, "volume": number_of_slides}
