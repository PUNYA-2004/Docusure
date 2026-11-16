import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any

class DocumentPreprocessor:
    """
    Image preprocessing suite for document degradation compensation:
    - Deskewing (angle estimation and affine rotation)
    - Denoising (Bilateral / Gaussian filter)
    - Contrast Enhancement (CLAHE)
    - Binarization & Adaptive Thresholding
    """

    @staticmethod
    def deskew(image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Calculates skew angle and rotates the image to upright orientation."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Find coordinates of all foreground pixels
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 50:
            return image, 0.0

        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        # If angle is very small, no rotation needed
        if abs(angle) < 0.3 or abs(angle) > 45:
            return image, 0.0

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated, float(angle)

    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """Applies CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
            return enhanced
        else:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            return clahe.apply(image)

    @staticmethod
    def denoise(image: np.ndarray) -> np.ndarray:
        """Removes scanner and sensor noise while preserving sharp font edges."""
        if len(image.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, 8, 8, 7, 21)
        return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

    @staticmethod
    def preprocess_pipeline(image_path: str, output_path: str) -> Dict[str, Any]:
        """Executes full diagnostic preprocessing on a degraded document."""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image at {image_path}")

        original_h, original_w = img.shape[:2]
        
        # 1. Deskew
        deskewed, skew_angle = DocumentPreprocessor.deskew(img)
        
        # 2. Contrast Enhancement
        enhanced = DocumentPreprocessor.enhance_contrast(deskewed)
        
        # 3. Denoise
        denoised = DocumentPreprocessor.denoise(enhanced)
        
        # Save output
        cv2.imwrite(output_path, denoised)
        
        return {
            "skew_angle": round(skew_angle, 2),
            "original_dimensions": [original_w, original_h],
            "enhanced": True,
            "denoised": True,
            "output_path": output_path
        }
