# Long Code Files Report

**Generated:** 2026-01-13
**Threshold:** 800+ lines

---

## Files Exceeding 800 Lines

| # | File Path | Lines | Status |
|---|-----------|-------|--------|
| 1 | `packages/services/video-tools/video_utils/ai_analysis_commands.py` | 1634 | Needs refactoring |
| 2 | `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py` | 1411 | Needs refactoring |
| 3 | `packages/services/video-tools/video_utils/video_understanding.py` | 1363 | Needs refactoring |
| 4 | `packages/providers/fal/text-to-image/fal_text_to_image_generator.py` | 892 | Needs refactoring |

**Total:** 4 files exceed the 800-line threshold

---

## Recommendations

Per project guidelines in CLAUDE.md:
> "Never create a file longer than 500 lines of code. If a file approaches this limit, refactor by splitting it into modules or helper files."

### Suggested Refactoring

#### 1. `ai_analysis_commands.py` (1634 lines)
- Split into separate command modules by functionality
- Create `commands/` subdirectory with individual command files
- Extract shared utilities to `command_utils.py`

#### 2. `executor.py` (1411 lines)
- Separate step execution logic into `step_executor.py`
- Extract parallel execution to `parallel_runner.py`
- Move result handling to `result_handler.py`

#### 3. `video_understanding.py` (1363 lines)
- Split analysis types into separate modules
- Create `analyzers/` subdirectory
- Extract prompts to `prompts.py`

#### 4. `fal_text_to_image_generator.py` (892 lines)
- Extract individual model implementations to separate files
- Create `models/` subdirectory similar to avatar module pattern
- Move shared utilities to `utils.py`

---

## Files Approaching Limit (500-800 lines)

| File Path | Lines |
|-----------|-------|
| `video_utils/command_dispatcher.py` | 769 |
| `fal/image-to-image/examples/demo.py` | 758 |
| `fal/image-to-video/fal_image_to_video_generator.py` | 754 |
| `video_utils/gemini_analyzer.py` | 752 |
| `video_utils/media_processing_controller.py` | 632 |
| `video_utils/enhanced_audio_processor.py` | 624 |
| `ai_content_pipeline/__main__.py` | 602 |
| `video_utils/openrouter_analyzer.py` | 589 |
| `ai_content_platform/core/parallel_executor.py` | 569 |
| `ai_content_platform/cli/commands.py` | 563 |

---

## Action Items

- [ ] Refactor `ai_analysis_commands.py` - Priority: High
- [ ] Refactor `executor.py` - Priority: High
- [ ] Refactor `video_understanding.py` - Priority: Medium
- [ ] Refactor `fal_text_to_image_generator.py` - Priority: Medium
- [ ] Monitor files approaching 500-line limit
