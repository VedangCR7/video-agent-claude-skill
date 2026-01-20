# Quick Reference Cheat Sheet

Fast reference for common commands, models, and patterns.

## CLI Commands

### Image Generation
```bash
# Basic
ai-content-pipeline generate-image --text "prompt" --model flux_dev

# With options
ai-content-pipeline generate-image \
  --text "sunset over mountains" \
  --model flux_dev \
  --aspect-ratio 16:9 \
  --output sunset.png

# Fast/cheap testing
ai-content-pipeline generate-image --text "test" --model flux_schnell

# Mock mode (free)
ai-content-pipeline generate-image --text "test" --mock
```

### Video Generation
```bash
# Text to video (full pipeline)
ai-content-pipeline create-video --text "ocean waves"

# Image to video
ai-content-pipeline image-to-video --image photo.png --model kling_2_6_pro

# Direct text to video
ai-content-pipeline text-to-video --text "flying drone" --model hailuo_pro
```

### Pipeline Operations
```bash
# Run pipeline
ai-content-pipeline run-chain --config pipeline.yaml --input "prompt"

# Dry run (validate)
ai-content-pipeline run-chain --config pipeline.yaml --dry-run

# Estimate cost
ai-content-pipeline estimate-cost --config pipeline.yaml

# Parallel execution
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml
```

### Utility Commands
```bash
# List models
ai-content-pipeline list-models

# Create examples
ai-content-pipeline create-examples

# Help
ai-content-pipeline --help
aicp --help  # Short alias
```

---

## Model Quick Reference

### Text-to-Image (by speed)
| Model | Speed | Cost | Quality |
|-------|-------|------|---------|
| `flux_schnell` | ★★★★★ | $0.001 | Good |
| `nano_banana_pro` | ★★★★ | $0.002 | Good |
| `flux_dev` | ★★★ | $0.003 | Great |
| `imagen4` | ★★ | $0.004 | Excellent |

### Image-to-Video (by cost)
| Model | Cost | Duration | Quality |
|-------|------|----------|---------|
| `hailuo` | $0.30 | 6s | Good |
| `kling_2_1` | $0.25-0.50 | 5s | Good |
| `kling_2_6_pro` | $0.50-1.00 | 5-10s | Great |
| `sora_2_pro` | $1.20-3.60 | 4-20s | Excellent |

### Text-to-Video (by cost)
| Model | Cost | Duration |
|-------|------|----------|
| `hailuo_pro` | $0.08 | 6s fixed |
| `kling_2_6_pro` | $0.35-1.40 | 5-10s |
| `sora_2` | $0.40-1.20 | 4-12s |

---

## YAML Pipeline Templates

### Basic Image
```yaml
name: "Image Generation"
steps:
  - name: "generate"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
```

### Image to Video
```yaml
name: "Image to Video"
steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
      aspect_ratio: "16:9"

  - name: "video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "image"
    params:
      duration: 5
```

### Parallel Batch
```yaml
name: "Batch Generation"
settings:
  parallel: true
steps:
  - type: "parallel_group"
    steps:
      - type: "text_to_image"
        params: { prompt: "image 1" }
      - type: "text_to_image"
        params: { prompt: "image 2" }
      - type: "text_to_image"
        params: { prompt: "image 3" }
```

---

## Python API

### Basic Usage
```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Generate image
result = manager.generate_image(prompt="sunset", model="flux_dev")
print(result.output_path)

# Create video
result = manager.create_video(prompt="ocean waves")
print(result.output_path)

# Run pipeline
results = manager.run_pipeline("config.yaml", input_text="my prompt")
```

### With Cost Tracking
```python
# Estimate first
estimate = manager.estimate_cost("pipeline.yaml")
print(f"Cost: ${estimate.total:.2f}")

# Then run
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
