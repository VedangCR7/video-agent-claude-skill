"""
Image analysis commands using Google Gemini.

Provides CLI commands for image description, classification, object detection,
text extraction (OCR), and composition analysis.
"""

from pathlib import Path
from typing import Optional

from ..command_utils import (
    check_and_report_gemini_status,
    setup_paths,
    select_analysis_type,
    get_analysis_options,
    process_files_with_progress,
    print_results_summary,
)
from ..file_utils import find_image_files
from ..ai_utils import analyze_image_file, save_analysis_result

# Supported image extensions (keep in sync with file_utils.py)
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.bmp', '.tiff', '.gif'}

# Analysis types for image
IMAGE_ANALYSIS_TYPES = {
    '1': ('description', 'Image description and visual analysis'),
    '2': ('classification', 'Image classification and categorization'),
    '3': ('objects', 'Object detection and identification'),
    '4': ('text', 'Text extraction (OCR) from images'),
    '5': ('composition', 'Artistic and technical composition analysis'),
    '6': ('qa', 'Question and answer analysis'),
}


def cmd_analyze_images() -> None:
    """Comprehensive image analysis using Gemini."""
    print("🖼️ IMAGE ANALYSIS - Google Gemini")
    print("=" * 50)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_image_files, "image", IMAGE_EXTENSIONS)
    if not paths:
        return

    print(f"🖼️ Found {len(paths.files)} image file(s)")

    analysis_type = select_analysis_type(IMAGE_ANALYSIS_TYPES)
    if not analysis_type:
        return

    config = get_analysis_options(analysis_type)

    def analyzer(file_path: Path):
        return analyze_image_file(
            file_path,
            config.analysis_type,
            questions=config.questions,
            detailed=config.detailed
        )

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix=f"_{analysis_type}_analysis",
        media_emoji="🖼️",
        analysis_type=analysis_type
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_describe_images() -> None:
    """Quick description of images using Gemini."""
    print("📝 IMAGE DESCRIPTION - Google Gemini")
    print("=" * 50)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_image_files, "image", IMAGE_EXTENSIONS)
    if not paths:
        return

    print(f"🖼️ Found {len(paths.files)} image file(s)")

    config = get_analysis_options('description')

    def analyzer(file_path: Path):
        from ..gemini_analyzer import GeminiVideoAnalyzer
        gemini_analyzer = GeminiVideoAnalyzer()
        return gemini_analyzer.describe_image(file_path, config.detailed)

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix="_description",
        media_emoji="🖼️",
        analysis_type="description"
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_extract_text() -> None:
    """Extract text from images using Gemini OCR."""
    print("📝 IMAGE TEXT EXTRACTION - Google Gemini OCR")
    print("=" * 50)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_image_files, "image", IMAGE_EXTENSIONS)
    if not paths:
        return

    print(f"🖼️ Found {len(paths.files)} image file(s)")

    def analyzer(file_path: Path):
        from ..gemini_analyzer import GeminiVideoAnalyzer
        gemini_analyzer = GeminiVideoAnalyzer()
        return gemini_analyzer.extract_text_from_image(file_path)

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix="_text",
        media_emoji="🖼️",
        analysis_type="text"
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_analyze_images_with_params(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    format_type: str = 'json'
) -> None:
    """Enhanced analyze-images command with parameter support.

    Args:
        input_path: Path to input image file or directory
        output_path: Path to output file or directory
        format_type: Output format ('json', 'txt')
    """
    print("🖼️ IMAGE ANALYSIS - Enhanced with Parameters")
    print("=" * 60)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(input_path, output_path, find_image_files, "image", IMAGE_EXTENSIONS)
    if not paths:
        return

    print(f"🖼️ Found {len(paths.files)} image file(s)")
    print(f"📁 Output directory: {paths.output_dir}")
    print(f"📋 Format: {format_type}")

    analysis_type = select_analysis_type(IMAGE_ANALYSIS_TYPES)
    if not analysis_type:
        return

    config = get_analysis_options(analysis_type)

    def analyzer(file_path: Path):
        return analyze_image_file(
            file_path,
            config.analysis_type,
            questions=config.questions,
            detailed=config.detailed
        )

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix=f"_{analysis_type}_analysis",
        media_emoji="🖼️",
        analysis_type=analysis_type
    )

    print_results_summary(successful, failed, paths.output_dir)
