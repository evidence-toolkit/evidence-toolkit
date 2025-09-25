#!/usr/bin/env python3
"""
Image Analyzer - OpenAI Vision API integration for image analysis
"""

import os
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import openai
from openai import OpenAI

from .unified_models import ImageAnalysisResult
from .utils import is_image_file


class ImageAnalyzer:
    """Analyzes images using OpenAI Vision API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-vision-preview",
        max_tokens: int = 1000
    ):
        """Initialize image analyzer"""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens

    def analyze_image(
        self,
        image_path: Path,
        prompt: Optional[str] = None
    ) -> ImageAnalysisResult:
        """Analyze an image using OpenAI Vision API"""
        if not is_image_file(image_path):
            raise ValueError(f"File {image_path} is not a supported image format")

        if not image_path.exists():
            raise ValueError(f"Image file {image_path} does not exist")

        # Default analysis prompt
        if prompt is None:
            prompt = """Analyze this image for legal evidence purposes. Provide:
1. A detailed description of what you see
2. Any text visible in the image
3. Objects, people, or locations that might be relevant
4. Any timestamps, dates, or identifying information
5. Overall assessment of the image's potential evidential value

Format your response as JSON with these fields:
- scene_description: string
- detected_text: string (if any)
- detected_objects: array of strings
- people_present: boolean
- timestamps_visible: boolean
- potential_evidence_value: string (low/medium/high)
- analysis_notes: string"""

        try:
            # Encode image to base64
            image_base64 = self._encode_image(image_path)

            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0  # Deterministic analysis
            )

            # Extract response content
            response_content = response.choices[0].message.content
            response_dict = response.model_dump()

            # Try to parse JSON response
            analysis_data = self._parse_response(response_content)

            return ImageAnalysisResult(
                openai_model=self.model,
                openai_response=response_dict,
                detected_objects=analysis_data.get("detected_objects"),
                detected_text=analysis_data.get("detected_text"),
                scene_description=analysis_data.get("scene_description"),
                analysis_confidence=self._calculate_confidence(response_dict)
            )

        except Exception as e:
            # Return error result
            return ImageAnalysisResult(
                openai_model=self.model,
                openai_response={"error": str(e)},
                detected_objects=None,
                detected_text=None,
                scene_description=f"Analysis failed: {str(e)}",
                analysis_confidence=0.0
            )

    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _parse_response(self, response_content: str) -> Dict[str, Any]:
        """Parse OpenAI response, handling both JSON and text formats"""
        import json

        try:
            # Try to parse as JSON
            return json.loads(response_content)
        except json.JSONDecodeError:
            # If not JSON, extract information from text
            return {
                "scene_description": response_content,
                "detected_text": self._extract_text_from_response(response_content),
                "detected_objects": self._extract_objects_from_response(response_content),
                "analysis_notes": "Response was not in JSON format, parsed from text"
            }

    def _extract_text_from_response(self, response: str) -> Optional[str]:
        """Extract mentioned text from response"""
        # Simple heuristic to find quoted text or text mentions
        import re

        text_patterns = [
            r'"([^"]*)"',  # Quoted text
            r'text[:\s]+([^\n\.]+)',  # Text mentions
            r'says[:\s]+"([^"]*)"'  # "Says" patterns
        ]

        for pattern in text_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                return '; '.join(matches)

        return None

    def _extract_objects_from_response(self, response: str) -> Optional[List[str]]:
        """Extract mentioned objects from response"""
        # Simple heuristic to find common object mentions
        common_objects = [
            "person", "people", "car", "vehicle", "building", "sign", "document",
            "phone", "computer", "camera", "table", "chair", "door", "window",
            "text", "number", "date", "timestamp", "logo", "badge", "license",
            "weapon", "money", "drugs", "evidence"
        ]

        found_objects = []
        response_lower = response.lower()

        for obj in common_objects:
            if obj in response_lower:
                found_objects.append(obj)

        return found_objects if found_objects else None

    def _calculate_confidence(self, response_dict: Dict[str, Any]) -> float:
        """Calculate confidence score based on response metadata"""
        try:
            # Simple confidence based on response length and completion reason
            usage = response_dict.get('usage', {})
            choices = response_dict.get('choices', [])

            if not choices:
                return 0.0

            finish_reason = choices[0].get('finish_reason')
            if finish_reason == 'stop':
                confidence = 0.8
            elif finish_reason == 'length':
                confidence = 0.6  # Truncated response
            else:
                confidence = 0.4

            # Adjust based on response length
            completion_tokens = usage.get('completion_tokens', 0)
            if completion_tokens > 500:
                confidence += 0.1
            elif completion_tokens < 100:
                confidence -= 0.2

            return max(0.0, min(1.0, confidence))

        except Exception:
            return 0.5  # Default confidence