"""
Audio analysis commands using Google Gemini.

Provides CLI commands for audio description, transcription, content analysis,
and event detection.
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
from ..file_utils import find_audio_files
from ..ai_utils import analyze_audio_file, save_analysis_result

# Supported audio extensions (keep in sync with file_utils.py)
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.aac', '.ogg', '.m4a', '.flac', '.wma'}

# Analysis types for audio
AUDIO_ANALYSIS_TYPES = {
    '1': ('description', 'Audio description and characteristics'),
    '2': ('transcription', 'Speech-to-text transcription'),
    '3': ('content_analysis', 'Comprehensive content analysis'),
    '4': ('events', 'Audio event and segment detection'),
    '5': ('qa', 'Question and answer analysis'),
}


def cmd_analyze_audio() -> None:
    """Comprehensive audio analysis using Gemini."""
    print("🔊 AUDIO ANALYSIS - Google Gemini")
    print("=" * 50)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_audio_files, "audio", AUDIO_EXTENSIONS)
    if not paths:
        return

    print(f"🎵 Found {len(paths.files)} audio file(s)")

    analysis_type = select_analysis_type(AUDIO_ANALYSIS_TYPES, default_key='2')
    if not analysis_type:
        return

    config = get_analysis_options(analysis_type)

    def analyzer(file_path: Path):
        return analyze_audio_file(
            file_path,
            config.analysis_type,
            questions=config.questions,
            detailed=config.detailed,
            speaker_identification=config.speaker_identification
        )

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix=f"_{analysis_type}_analysis",
        media_emoji="🎵",
        analysis_type=analysis_type
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_transcribe_audio() -> None:
    """Quick transcription of audio files using Gemini."""
    print("🎤 AUDIO TRANSCRIPTION - Google Gemini")
    print("=" * 50)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_audio_files, "audio", AUDIO_EXTENSIONS)
    if not paths:
        return

    print(f"🎵 Found {len(paths.files)} audio file(s)")

    config = get_analysis_options('transcription')

    def analyzer(file_path: Path):
        from ..gemini_analyzer import GeminiVideoAnalyzer
        gemini_analyzer = GeminiVideoAnalyzer()
        return gemini_analyzer.transcribe_audio(
            file_path,
            config.include_timestamps,
            config.speaker_identification
        )

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix="_transcription",
        media_emoji="🎵",
        analysis_type="transcription"
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_describe_audio() -> None:
    """Quick description of audio files using Gemini."""
    print("📝 AUDIO DESCRIPTION - Google Gemini")
    print("=" * 50)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(None, None, find_audio_files, "audio", AUDIO_EXTENSIONS)
    if not paths:
        return

    print(f"🎵 Found {len(paths.files)} audio file(s)")

    config = get_analysis_options('description')

    def analyzer(file_path: Path):
        from ..gemini_analyzer import GeminiVideoAnalyzer
        gemini_analyzer = GeminiVideoAnalyzer()
        return gemini_analyzer.describe_audio(file_path, config.detailed)

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix="_description",
        media_emoji="🎵",
        analysis_type="description"
    )

    print_results_summary(successful, failed, paths.output_dir)


def cmd_analyze_audio_with_params(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    format_type: str = 'json'
) -> None:
    """Enhanced analyze-audio command with parameter support.

    Args:
        input_path: Path to input audio file or directory
        output_path: Path to output file or directory
        format_type: Output format ('json', 'txt')
    """
    print("🔊 AUDIO ANALYSIS - Enhanced with Parameters")
    print("=" * 60)

    if not check_and_report_gemini_status():
        return

    paths = setup_paths(input_path, output_path, find_audio_files, "audio", AUDIO_EXTENSIONS)
    if not paths:
        return

    print(f"🎵 Found {len(paths.files)} audio file(s)")
    print(f"📁 Output directory: {paths.output_dir}")
    print(f"📋 Format: {format_type}")

    analysis_type = select_analysis_type(AUDIO_ANALYSIS_TYPES, default_key='2')
    if not analysis_type:
        return

    config = get_analysis_options(analysis_type)

    def analyzer(file_path: Path):
        return analyze_audio_file(
            file_path,
            config.analysis_type,
            questions=config.questions,
            detailed=config.detailed,
            speaker_identification=config.speaker_identification
        )

    successful, failed = process_files_with_progress(
        files=paths.files,
        analyzer_fn=analyzer,
        save_fn=save_analysis_result,
        output_dir=paths.output_dir,
        output_suffix=f"_{analysis_type}_analysis",
        media_emoji="🎵",
        analysis_type=analysis_type
    )

    print_results_summary(successful, failed, paths.output_dir)
