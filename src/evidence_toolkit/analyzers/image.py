#!/usr/bin/env python3
"""
Image Analyzer - OpenAI Vision API integration for image analysis (v3.0)

Part of Evidence Toolkit v3.0 unified architecture.

v3.3.1 Enhancement: Async batch processing for parallel image analysis
"""

import os
import base64
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import openai
from openai import OpenAI, AsyncOpenAI

from evidence_toolkit.core.models import ImageAnalysisResult, ImageAnalysisStructured
from evidence_toolkit.core.utils import is_image_file


class ImageAnalyzer:
    """Analyzes images using OpenAI Vision API with async batch processing support"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",  # Cost-effective vision model with 1M+ context (fixed from gpt-4.1-mini)
        max_tokens: int = 1000,
        verbose: bool = True
    ):
        """Initialize image analyzer with Responses API support

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Vision-capable model (default: gpt-4o-mini - best balance of cost/quality)
            max_tokens: Maximum tokens for response (unused with Responses API)
            verbose: Print progress messages
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)  # For async operations
        self.model = model
        self.max_tokens = max_tokens
        self.verbose = verbose

    def analyze_pdf(
        self,
        pdf_path: Path,
        prompt: Optional[str] = None,
        max_pages: Optional[int] = None
    ) -> ImageAnalysisResult:
        """Analyze a scanned PDF by converting pages to images and analyzing with vision AI"""
        try:
            from pdf2image import convert_from_path
            import tempfile

            if self.verbose:
                print(f"📄 Converting PDF pages to images for vision analysis...")

            # Convert PDF pages to images
            images = convert_from_path(pdf_path, dpi=200)

            if max_pages:
                images = images[:max_pages]

            if self.verbose:
                print(f"   Found {len(images)} pages to analyze")

            # Analyze each page
            all_detected_text = []
            all_detected_objects = []
            scene_descriptions = []

            for i, page_image in enumerate(images, 1):
                if self.verbose and i % 5 == 0:
                    print(f"   Analyzing page {i}/{len(images)}...")

                # Save page to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    page_image.save(tmp.name, 'PNG')
                    tmp_path = Path(tmp.name)

                try:
                    # Analyze page as image
                    page_result = self.analyze_image(tmp_path, prompt)

                    # Collect results
                    if page_result.detected_text:
                        all_detected_text.append(f"[Page {i}] {page_result.detected_text}")
                    if page_result.detected_objects:
                        all_detected_objects.extend(page_result.detected_objects)
                    if page_result.scene_description:
                        scene_descriptions.append(f"Page {i}: {page_result.scene_description}")

                finally:
                    # Clean up temp file
                    tmp_path.unlink(missing_ok=True)

            # Combine results from all pages
            combined_text = "\n\n".join(all_detected_text) if all_detected_text else None
            combined_description = "\n\n".join(scene_descriptions) if scene_descriptions else None
            unique_objects = list(set(all_detected_objects)) if all_detected_objects else None

            if self.verbose:
                print(f"✅ Completed PDF analysis: {len(images)} pages")
                if combined_text:
                    print(f"   Extracted text from {len(all_detected_text)} pages")

            return ImageAnalysisResult(
                openai_model=self.model,
                openai_response={"pages_analyzed": len(images), "method": "pdf2image+responses_api"},
                detected_objects=unique_objects,
                detected_text=combined_text,
                scene_description=combined_description,
                analysis_confidence=0.8  # High confidence for multi-page analysis
            )

        except ImportError:
            return ImageAnalysisResult(
                openai_model=self.model,
                openai_response={"error": "pdf2image not installed - cannot analyze scanned PDFs"},
                detected_objects=None,
                detected_text=None,
                scene_description="PDF analysis failed: pdf2image library not available",
                analysis_confidence=0.0
            )
        except Exception as e:
            return ImageAnalysisResult(
                openai_model=self.model,
                openai_response={"error": str(e)},
                detected_objects=None,
                detected_text=None,
                scene_description=f"PDF analysis failed: {str(e)}",
                analysis_confidence=0.0
            )

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

        # Import legal domain prompt
        from evidence_toolkit.domains import legal_config
        system_prompt = legal_config.IMAGE_ANALYSIS_PROMPT

        try:
            # Encode image to base64
            image_base64 = self._encode_image(image_path)

            # Call OpenAI Responses API with structured outputs (SAME PATTERN as DocumentAnalyzer/EmailAnalyzer)
            response = self.client.responses.parse(
                model=self.model,  # Vision-capable model (default: gpt-4o-2024-08-06)
                input=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",  # Responses API format (not "image_url")
                                "image_url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        ]
                    }
                ],
                text_format=ImageAnalysisStructured  # Pydantic model for structured output
            )

            # Handle response (SAME PATTERN as DocumentAnalyzer, EmailAnalyzer)
            if response.status == "completed" and response.output_parsed:
                if self.verbose:
                    print(f"✅ Image analysis complete - confidence: {response.output_parsed.confidence_overall:.2f}")

                # Convert structured Pydantic model to legacy ImageAnalysisResult format
                return ImageAnalysisResult(
                    openai_model=self.model,
                    openai_response={"parsed": response.output_parsed.model_dump()},
                    detected_objects=response.output_parsed.detected_objects,
                    detected_text=response.output_parsed.detected_text,
                    scene_description=response.output_parsed.scene_description,
                    analysis_confidence=response.output_parsed.confidence_overall
                )
            elif response.status == "incomplete":
                if self.verbose:
                    print(f"❌ Image analysis incomplete: {response.incomplete_details}")
                return ImageAnalysisResult(
                    openai_model=self.model,
                    openai_response={"error": f"incomplete: {response.incomplete_details}"},
                    detected_objects=None,
                    detected_text=None,
                    scene_description="Image analysis incomplete",
                    analysis_confidence=0.0
                )
            else:
                # Check for refusal (SAME PATTERN as other analyzers)
                if (response.output and len(response.output) > 0 and
                    len(response.output[0].content) > 0 and
                    response.output[0].content[0].type == "refusal"):
                    refusal_msg = response.output[0].content[0].refusal
                    if self.verbose:
                        print(f"❌ Image analysis refused: {refusal_msg}")
                    return ImageAnalysisResult(
                        openai_model=self.model,
                        openai_response={"error": f"refusal: {refusal_msg}"},
                        detected_objects=None,
                        detected_text=None,
                        scene_description=f"Analysis refused: {refusal_msg}",
                        analysis_confidence=0.0
                    )
                raise Exception("Image analysis failed with unknown error")

        except Exception as e:
            # Return error result
            if self.verbose:
                print(f"❌ Image analysis error: {str(e)}")
            return ImageAnalysisResult(
                openai_model=self.model,
                openai_response={"error": str(e)},
                detected_objects=None,
                detected_text=None,
                scene_description=f"Analysis failed: {str(e)}",
                analysis_confidence=0.0
            )

    async def analyze_image_async(
        self,
        image_path: Path,
        prompt: Optional[str] = None
    ) -> ImageAnalysisResult:
        """Async version of analyze_image for batch processing

        This method allows multiple images to be analyzed concurrently,
        significantly speeding up processing for cases with many images.

        Args:
            image_path: Path to image file
            prompt: Optional custom prompt (unused, uses legal_config)

        Returns:
            ImageAnalysisResult object
        """
        if not is_image_file(image_path):
            raise ValueError(f"File {image_path} is not a supported image format")

        if not image_path.exists():
            raise ValueError(f"Image file {image_path} does not exist")

        # Import legal domain prompt
        from evidence_toolkit.domains import legal_config
        system_prompt = legal_config.IMAGE_ANALYSIS_PROMPT

        try:
            # Encode image to base64 (sync operation, but fast)
            image_base64 = self._encode_image(image_path)

            # Call OpenAI Responses API with structured outputs (ASYNC)
            response = await self.async_client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        ]
                    }
                ],
                text_format=ImageAnalysisStructured
            )

            # Handle response (same pattern as sync version)
            if response.status == "completed" and response.output_parsed:
                if self.verbose:
                    print(f"✅ Image analysis complete - confidence: {response.output_parsed.confidence_overall:.2f}")

                return ImageAnalysisResult(
                    openai_model=self.model,
                    openai_response={"parsed": response.output_parsed.model_dump()},
                    detected_objects=response.output_parsed.detected_objects,
                    detected_text=response.output_parsed.detected_text,
                    scene_description=response.output_parsed.scene_description,
                    analysis_confidence=response.output_parsed.confidence_overall
                )
            elif response.status == "incomplete":
                if self.verbose:
                    print(f"❌ Image analysis incomplete: {response.incomplete_details}")
                return ImageAnalysisResult(
                    openai_model=self.model,
                    openai_response={"error": f"incomplete: {response.incomplete_details}"},
                    detected_objects=None,
                    detected_text=None,
                    scene_description="Image analysis incomplete",
                    analysis_confidence=0.0
                )
            else:
                raise Exception("Image analysis failed with unknown error")

        except Exception as e:
            if self.verbose:
                print(f"❌ Image analysis error: {str(e)}")
            return ImageAnalysisResult(
                openai_model=self.model,
                openai_response={"error": str(e)},
                detected_objects=None,
                detected_text=None,
                scene_description=f"Analysis failed: {str(e)}",
                analysis_confidence=0.0
            )

    async def analyze_images_batch(
        self,
        image_paths: List[Path],
        max_concurrent: int = 5,
        quiet: bool = False
    ) -> List[ImageAnalysisResult]:
        """Analyze multiple images concurrently with rate limiting

        This is the main entry point for batch processing. It uses asyncio
        to process multiple images in parallel while respecting rate limits.

        Args:
            image_paths: List of image file paths to analyze
            max_concurrent: Maximum number of concurrent API calls (default: 5)
            quiet: Suppress progress output

        Returns:
            List of ImageAnalysisResult objects in same order as input paths

        Example:
            >>> analyzer = ImageAnalyzer()
            >>> paths = [Path("img1.jpg"), Path("img2.png")]
            >>> results = asyncio.run(analyzer.analyze_images_batch(paths))
        """
        if not image_paths:
            return []

        if not quiet:
            print(f"🖼️  Batch processing {len(image_paths)} images (max {max_concurrent} concurrent)...")

        # Create semaphore to limit concurrent API calls
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_with_semaphore(path: Path, index: int) -> ImageAnalysisResult:
            """Analyze one image with semaphore rate limiting"""
            async with semaphore:
                if not quiet and (index + 1) % 5 == 0:
                    print(f"   Processing image {index + 1}/{len(image_paths)}...")

                try:
                    return await self.analyze_image_async(path)
                except Exception as e:
                    # Return error result instead of raising
                    return ImageAnalysisResult(
                        openai_model=self.model,
                        openai_response={"error": str(e)},
                        detected_objects=None,
                        detected_text=None,
                        scene_description=f"Batch analysis failed: {str(e)}",
                        analysis_confidence=0.0
                    )

        # Process all images concurrently (with semaphore limiting)
        tasks = [analyze_with_semaphore(path, i) for i, path in enumerate(image_paths)]
        results = await asyncio.gather(*tasks)

        if not quiet:
            successful = sum(1 for r in results if r.analysis_confidence > 0.0)
            print(f"✅ Batch complete: {successful}/{len(results)} successful")

        return results

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
