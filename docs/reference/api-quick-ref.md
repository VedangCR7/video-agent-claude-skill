# API Quick Reference

> **This is a condensed reference.** For complete documentation with all parameters, see:
> - **[Python API Reference](../api/python-api.md)** - Full API documentation
> - **[CLI Commands Reference](cli-commands.md)** - Full CLI documentation

---

## Python API

### Import

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager
manager = AIPipelineManager()
```

### Image Generation

```python
# Generate image from text
result = manager.generate_image(
    prompt="description",           # Required
    model="flux_dev",               # Optional, default: flux_dev
    aspect_ratio="16:9",            # Optional
    num_images=1,                   # Optional
    output_dir="output/"            # Optional
)

# Returns
result.success          # bool
result.output_path      # str
result.cost             # float
result.model            # str
result.metadata         # dict
```

### Image-to-Image

```python
# Transform existing image
result = manager.transform_image(
    input_path="input.png",         # Required
    prompt="modifications",         # Required
    model="photon_flash",           # Optional
    strength=0.7                    # Optional, 0.0-1.0
)
```

### Video Generation

```python
# Text to video (direct)
result = manager.text_to_video(
    prompt="description",           # Required
    model="hailuo_pro",             # Optional
    duration=6                      # Optional, seconds
)

# Image to video
result = manager.image_to_video(
    input_path="image.png",         # Required
    prompt="motion description",    # Optional
    model="kling_2_6_pro",          # Optional
    duration=5                      # Optional
)

# Full pipeline (text → image → video)
result = manager.create_video(
    prompt="description",           # Required
    image_model="flux_dev",         # Optional
    video_model="kling_2_6_pro"     # Optional
)
```

### Video Analysis

```python
# Analyze video content
result = manager.analyze_video(
    input_path="video.mp4",         # Required
    model="gemini-3-pro",           # Optional
    analysis_type="timeline"        # timeline|describe|transcribe
)

# Returns
result.analysis         # str (analysis text)
result.video_duration   # float (seconds)
```

### Pipeline Execution

```python
# Run from config file
results = manager.run_pipeline(
    config_path="pipeline.yaml",    # Required
    input_text="prompt",            # Optional
    dry_run=False                   # Optional
)

# Run from dict
results = manager.run_pipeline(
    config={
        "name": "Pipeline",
        "steps": [...]
    },
    input_text="prompt"
)

# Returns list of StepResult objects
for step in results:
    print(step.step_name)
    print(step.output_path)
    print(step.cost)
```

### Cost Estimation

```python
# Estimate before running
estimate = manager.estimate_cost(
    config_path="pipeline.yaml",    # Required
    input_text="prompt"             # Optional
)

# Returns
estimate.total          # float (total cost)
estimate.steps          # list (per-step costs)
estimate.breakdown      # dict (detailed breakdown)
```

### Utility Methods

```python
# List available models
models = manager.list_models(
    category="text_to_image"        # Optional filter
)

# Validate configuration
is_valid = manager.validate_config("pipeline.yaml")

# Get model info
info = manager.get_model_info("flux_dev")
```

---

## CLI Commands

For complete CLI reference, see **[CLI Commands Reference](cli-commands.md)**.

Quick examples:
```bash
aicp generate-image --text "prompt" --model flux_dev
aicp create-video --text "prompt"
aicp run-chain --config pipeline.yaml
aicp list-models
```

---

## YAML Configuration

For complete YAML reference, see **[YAML Pipelines Guide](../guides/pipelines/yaml-pipelines.md)**.

Quick template:
```yaml
name: "Pipeline Name"
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

**Step types:** `text_to_image`, `image_to_image`, `text_to_video`, `image_to_video`, `video_analysis`, `text_to_speech`, `video_upscale`, `parallel_group`

---

## Models Quick Reference

For complete model reference, see **[Models Reference](models.md)**.

| Category | Budget | Standard | Premium |
|----------|--------|----------|---------|
| Text-to-Image | `flux_schnell` $0.001 | `flux_dev` $0.003 | `imagen4` $0.004 |
| Image-to-Video | `hailuo` $0.30 | `kling_2_6_pro` $0.50 | `sora_2_pro` $1.20 |
| Text-to-Video | `hailuo_pro` $0.08 | `kling_2_6_pro` $0.35 | `sora_2` $0.40 |

---

## Environment Variables

```bash
# Required
FAL_KEY=your_fal_key

# Optional
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENROUTER_API_KEY=your_openrouter_key

# Settings
PIPELINE_PARALLEL_ENABLED=true
PIPELINE_LOG_LEVEL=INFO
```

---

## Result Objects

### ImageResult

```python
result.success          # bool
result.output_path      # str
result.cost             # float
result.model            # str
result.prompt           # str
result.aspect_ratio     # str
result.metadata         # dict
```

### VideoResult

```python
result.success          # bool
result.output_path      # str
result.cost             # float
result.model            # str
result.duration         # float
result.metadata         # dict
```

### PipelineResult

```python
result.success          # bool
result.total_cost       # float
result.steps            # list[StepResult]
result.outputs          # list[str]
result.execution_time   # float
```

### StepResult

```python
step.step_name          # str
step.step_type          # str
step.success            # bool
step.output_path        # str
step.cost               # float
step.error              # str | None
```

---

[Back to Documentation Index](../index.md)
