# Quick Reference Cheat Sheet

Fast reference for common commands, models, and patterns.

> **See also:** [API Quick Reference](api-quick-ref.md) for Python API methods and result objects.

## CLI Commands

> Full reference: **[CLI Commands Reference](cli-commands.md)**

### Essential Commands
```bash
# Image generation
aicp generate-image --text "prompt" --model flux_dev
aicp generate-image --text "test" --mock          # Free testing

# Video generation
aicp create-video --text "ocean waves"            # Text → Image → Video
aicp image-to-video --image photo.png             # Image → Video
aicp text-to-video --text "prompt"                # Direct text → video

# Pipelines
aicp run-chain --config pipeline.yaml --input "prompt"
aicp estimate-cost --config pipeline.yaml         # Check cost first

# Utilities
aicp list-models                                  # See available models
aicp --help                                       # Full help
```

---

## Model Quick Reference

> Full reference: **[Models Reference](models.md)**

| Category | Budget | Standard | Premium |
|----------|--------|----------|---------|
| Text-to-Image | `flux_schnell` $0.001 | `flux_dev` $0.003 | `imagen4` $0.004 |
| Image-to-Video | `hailuo` $0.30 | `kling_2_6_pro` $0.50 | `sora_2_pro` $1.20 |
| Text-to-Video | `hailuo_pro` $0.08 | `kling_2_6_pro` $0.35 | `sora_2` $0.40 |

---

## YAML Pipeline Templates

> Full reference: **[YAML Pipelines Guide](../guides/pipelines/yaml-pipelines.md)**

```yaml
name: "Image to Video"
steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
  - name: "video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "image"
```

---

## Python API

> Full reference: **[Python API Reference](../api/python-api.md)**

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Generate image
result = manager.generate_image(prompt="sunset", model="flux_dev")

# Create video
result = manager.create_video(prompt="ocean waves")

# Run pipeline
results = manager.run_pipeline("config.yaml", input_text="my prompt")

# Estimate cost first
estimate = manager.estimate_cost("pipeline.yaml")
if estimate.total < 1.00:
    results = manager.run_pipeline("pipeline.yaml")
```

---

## Environment Variables

```bash
# Required
FAL_KEY=your_fal_api_key

# Optional
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENROUTER_API_KEY=your_openrouter_key

# Pipeline settings
PIPELINE_PARALLEL_ENABLED=true
PIPELINE_LOG_LEVEL=INFO
```

---

## Prompt Formulas

### Image Prompt
```
[Subject] + [Details] + [Environment] + [Style] + [Quality]

Example:
"golden retriever puppy, playing in leaves, autumn park,
natural photography, sharp focus, 4k"
```

### Video Motion Prompt
```
[Camera movement] + [Subject motion] + [Speed] + [Atmosphere]

Example:
"slow pan left, gentle breeze moving hair, smooth motion, peaceful"
```

---

## Common Patterns

### Development → Production
```bash
# Development (cheap)
--model flux_schnell  # $0.001

# Testing (quality check)
--model flux_dev      # $0.003

# Production (final)
--model imagen4       # $0.004
```

### Aspect Ratios
```yaml
# Landscape (YouTube, presentations)
aspect_ratio: "16:9"

# Portrait (Stories, TikTok)
aspect_ratio: "9:16"

# Square (Instagram posts)
aspect_ratio: "1:1"

# Cinematic
aspect_ratio: "2.39:1"
```

---

## Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Command not found | `pip install video-ai-studio` |
| API key error | Check `.env` file exists |
| Model not found | `ai-content-pipeline list-models` |
| Rate limited | Wait 30s, reduce workers |
| Timeout | Use faster model or retry |

---

## Cost Quick Reference

| Operation | Budget | Standard | Premium |
|-----------|--------|----------|---------|
| 1 image | $0.001 | $0.003 | $0.004 |
| 10 images | $0.01 | $0.03 | $0.04 |
| 1 video | $0.08 | $0.50 | $1.20 |
| 10 videos | $0.80 | $5.00 | $12.00 |

---

## File Locations

```
project/
├── .env              # API keys
├── pipeline.yaml     # Pipeline config
├── output/           # Generated files
│   ├── images/
│   └── videos/
└── .gitignore        # Include .env!
```

---

[Back to Documentation Index](../index.md)
