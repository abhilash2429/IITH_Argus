"""
Qwen2.5-VL OCR adapter.

Primary OCR path:
- Qwen2.5-VL via Hugging Face router (OpenAI-compatible endpoint)

Fallback:
- pytesseract local OCR (best-effort)
"""

from __future__ import annotations

import base64
import io
import json
import re
from dataclasses import dataclass
from typing import Any, Optional

import fitz
from PIL import Image

from backend.config import settings


@dataclass
class OCRResult:
    text: str
    confidence: float
    method: str


class QwenVLOCR:
    """
    Qwen2.5-VL OCR extraction client with local fallback.
    """

    def __init__(self) -> None:
        self.api_key = settings.huggingface_api_token or settings.qwen_vl_api_key
        self.base_url = settings.qwen_vl_base_url.rstrip("/")
        self.model = settings.qwen_vl_model
        self.timeout = settings.qwen_vl_timeout_sec

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    def extract_text_from_pdf(self, file_path: str) -> OCRResult:
        """
        OCR every page of a PDF by rendering to images and sending to Qwen2.5-VL.
        """
        text_chunks: list[str] = []
        confidences: list[float] = []

        with fitz.open(file_path) as doc:
            for page in doc:
                # Render at higher DPI equivalent for OCR quality.
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                result = self.extract_text_from_image(image)
                if result.text.strip():
                    text_chunks.append(result.text)
                confidences.append(result.confidence)

        joined = "\n".join(text_chunks).strip()
        if joined:
            avg_conf = sum(confidences) / max(len(confidences), 1)
            method = "qwen2.5-vl"
            if any(c < 0.55 for c in confidences):
                method = "qwen2.5-vl+fallback"
            return OCRResult(text=joined, confidence=max(0.35, min(0.98, avg_conf)), method=method)

        return self._fallback_pdf_tesseract(file_path)

    def extract_text_from_image_path(self, file_path: str) -> OCRResult:
        image = Image.open(file_path).convert("RGB")
        result = self.extract_text_from_image(image)
        if result.text.strip():
            return result
        return self._fallback_image_tesseract(image)

    def extract_text_from_image(self, image: Image.Image) -> OCRResult:
        if not self.enabled:
            return self._fallback_image_tesseract(image)

        image_b64 = self._encode_image(image)
        prompt = (
            "You are an OCR engine for Indian financial documents. Extract all visible text exactly. "
            "Keep numbers and table rows intact where possible. Return JSON only with keys: "
            '{"text": "...", "confidence": 0.0}'
        )
        payload = {
            "temperature": 0,
            "max_tokens": 2000,
        }

        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
            response = client.chat.completions.create(
                model=self.model,
                temperature=payload["temperature"],
                max_tokens=payload["max_tokens"],
                messages=[
                    {"role": "system", "content": "You are a high-accuracy OCR model."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                            },
                        ],
                    },
                ],
            )
            raw_content = response.choices[0].message.content or ""
            parsed = self._parse_ocr_json(raw_content)
            if parsed and parsed.get("text"):
                return OCRResult(
                    text=str(parsed.get("text", "")).strip(),
                    confidence=self._coerce_confidence(parsed.get("confidence"), default=0.82),
                    method="qwen2.5-vl",
                )

            clean = (raw_content or "").strip()
            if clean:
                return OCRResult(text=clean, confidence=0.68, method="qwen2.5-vl")
        except Exception:
            # Swallow and fallback to keep demo flow resilient.
            pass

        return self._fallback_image_tesseract(image)

    @staticmethod
    def _encode_image(image: Image.Image) -> str:
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=92)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    @staticmethod
    def _parse_ocr_json(content: str) -> Optional[dict[str, Any]]:
        if not content:
            return None
        stripped = content.strip()
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
        try:
            obj = json.loads(stripped)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass

        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    @staticmethod
    def _coerce_confidence(value: Any, *, default: float) -> float:
        try:
            conf = float(value)
        except (TypeError, ValueError):
            conf = default
        return max(0.05, min(0.99, conf))

    def _fallback_pdf_tesseract(self, file_path: str) -> OCRResult:
        text_chunks: list[str] = []
        confidences: list[float] = []

        with fitz.open(file_path) as doc:
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                fallback = self._fallback_image_tesseract(image)
                if fallback.text.strip():
                    text_chunks.append(fallback.text)
                confidences.append(fallback.confidence)

        return OCRResult(
            text="\n".join(text_chunks).strip(),
            confidence=sum(confidences) / max(len(confidences), 1) if confidences else 0.2,
            method="tesseract_fallback",
        )

    @staticmethod
    def _fallback_image_tesseract(image: Image.Image) -> OCRResult:
        try:
            import pytesseract

            text = pytesseract.image_to_string(image, lang="eng+hin")
            if text and text.strip():
                return OCRResult(text=text.strip(), confidence=0.5, method="tesseract_fallback")
        except Exception:
            pass
        return OCRResult(text="", confidence=0.2, method="ocr_unavailable")
