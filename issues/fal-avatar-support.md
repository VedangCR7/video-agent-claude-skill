# FAL Avatar & Video-to-Video Support Implementation

**Created:** 2026-01-13
**Branch:** `avatar`
**Status:** Planning
**Estimated Effort:** 4-6 hours (split into subtasks)

---

## Overview

Add comprehensive FAL avatar model support to the AI Content Pipeline, including:
- **OmniHuman v1.5** - Audio-driven human animation
- **VEED Fabric 1.0** - Lipsync video generation (image + audio)
- **VEED Fabric 1.0 Text** - Text-to-speech avatar videos
- **Kling O1 Video-to-Video Reference** - Style-guided video generation
- **Kling O1 Video-to-Video Edit** - Targeted video modifications

---

## API Specifications

### 1. OmniHuman v1.5 (`fal-ai/bytedance/omnihuman/v1.5`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_url` | string | Yes | Human figure image URL |
| `audio_url` | string | Yes | Audio file (max 30s @1080p, 60s @720p) |
| `prompt` | string | No | Text guidance for generation |
| `turbo_mode` | boolean | No | Faster with slight quality trade-off |
| `resolution` | enum | No | "720p" or "1080p" (default: 1080p) |

**Pricing:** $0.16/second
**Output:** `{ video: { url }, duration }`

---

### 2. VEED Fabric 1.0 (`veed/fabric-1.0`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_url` | string | Yes | Image source URL |
| `audio_url` | string | Yes | Audio file URL |
| `resolution` | enum | Yes | "720p" or "480p" |

**Pricing:** $0.08/sec (480p), $0.15/sec (720p)
**Fast variant:** +25% cost
**Output:** `{ url, content_type, file_name, file_size }`

---

### 3. VEED Fabric 1.0 Text (`veed/fabric-1.0/text`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_url` | string | Yes | Image source URL |
| `text` | string | Yes | Speech text (max 2000 chars) |
| `resolution` | enum | Yes | "720p" or "480p" |
| `voice_description` | string | No | Voice characteristics |

**Pricing:** $0.08/sec (480p), $0.15/sec (720p)
**Output:** `{ video: { url, content_type } }`

---

### 4. Kling O1 Video-to-Video Reference (`fal-ai/kling-video/o1/standard/video-to-video/reference`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Use `@Video1` to reference input |
| `video_url` | string | Yes | Reference video URL |
| `sound_url` | string | No | Audio URL (.mp3/.wav/.m4a, max 5MB) |
| `sound_start_time` | int | No | Audio start time (ms) |
| `sound_end_time` | int | No | Audio end time (ms) |
| `sound_insert_time` | int | No | Insert audio at time (ms) |
| `face_id` | string | No | Face ID from identify_face API |

**Pricing:** ~$0.10/second (estimated)
**Constraint:** 10-second max output per generation

---

### 5. Kling O1 Video-to-Video Edit (`fal-ai/kling-video/o1/standard/video-to-video/edit`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video_url` | string | Yes | Source video URL |
| `prompt` | string | Yes | Edit instructions |
| `mask_url` | string | No | Region mask for edits |

**Pricing:** ~$0.10/second (estimated)
**Use Case:** Targeted modifications without full regeneration

---

## Implementation Subtasks

### Subtask 1: Create Avatar Model Classes (1-1.5 hours)

**Goal:** Implement individual model classes following existing patterns

**Files to Create:**
```
packages/providers/fal/avatar-generation/
├── fal_avatar/
│   ├── __init__.py
│   ├── config/
│   │   └── constants.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                    # BaseAvatarModel
│   │   ├── omnihuman.py               # OmniHumanModel
│   │   ├── fabric.py                  # FabricModel, FabricTextModel
│   │   └── kling_v2v.py               # KlingReferenceModel, KlingEditModel
│   ├── utils/
│   │   └── validators.py
│   └── generator.py                   # FALAvatarGenerator
```

**Pattern Reference:** `packages/providers/fal/image-to-video/fal_image_to_video/models/veo.py`

**Implementation Details:**

1. **`base.py`** - Abstract base class:
```python
class BaseAvatarModel(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.endpoint = ""
        self.pricing = {}

    @abstractmethod
    def generate(self, **kwargs) -> Dict[str, Any]: pass

    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]: pass

    @abstractmethod
    def estimate_cost(self, duration: float, **kwargs) -> float: pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]: pass
```

2. **`omnihuman.py`** - OmniHuman v1.5:
```python
class OmniHumanModel(BaseAvatarModel):
    def __init__(self):
        super().__init__("omnihuman_v1_5")
        self.endpoint = "fal-ai/bytedance/omnihuman/v1.5"
        self.pricing = {"per_second": 0.16}
```

3. **`fabric.py`** - VEED Fabric models:
```python
class FabricModel(BaseAvatarModel):
    def __init__(self):
        super().__init__("fabric_1_0")
        self.endpoint = "veed/fabric-1.0"
        self.pricing = {"480p": 0.08, "720p": 0.15}

class FabricTextModel(BaseAvatarModel):
    def __init__(self):
        super().__init__("fabric_1_0_text")
        self.endpoint = "veed/fabric-1.0/text"
        self.pricing = {"480p": 0.08, "720p": 0.15}
```

4. **`kling_v2v.py`** - Kling video-to-video:
```python
class KlingReferenceModel(BaseAvatarModel):
    def __init__(self):
        super().__init__("kling_v2v_reference")
        self.endpoint = "fal-ai/kling-video/o1/standard/video-to-video/reference"
        self.pricing = {"per_second": 0.10}

class KlingEditModel(BaseAvatarModel):
    def __init__(self):
        super().__init__("kling_v2v_edit")
        self.endpoint = "fal-ai/kling-video/o1/standard/video-to-video/edit"
        self.pricing = {"per_second": 0.10}
```

---

### Subtask 2: Create Unified Generator (45 min - 1 hour)

**Goal:** Create generator that routes to appropriate model

**File:** `packages/providers/fal/avatar-generation/fal_avatar/generator.py`

**Pattern Reference:** `packages/providers/fal/image-to-video/fal_image_to_video/generator.py`

```python
class FALAvatarGenerator:
    def __init__(self):
        self.models = {
            "omnihuman_v1_5": OmniHumanModel(),
            "fabric_1_0": FabricModel(),
            "fabric_1_0_text": FabricTextModel(),
            "kling_v2v_reference": KlingReferenceModel(),
            "kling_v2v_edit": KlingEditModel(),
        }

    def generate_avatar(
        self,
        model: str = "omnihuman_v1_5",
        image_url: str = None,
        audio_url: str = None,
        video_url: str = None,
        text: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate avatar/video based on model type"""

    def list_models(self) -> List[str]:
        return list(self.models.keys())

    def get_model_info(self, model: str) -> Dict[str, Any]:
        return self.models[model].get_model_info()

    def estimate_cost(self, model: str, duration: float, **kwargs) -> float:
        return self.models[model].estimate_cost(duration, **kwargs)
```

---

### Subtask 3: Integrate with Core Pipeline (45 min - 1 hour)

**Goal:** Register models in core constants and update pipeline manager

**Files to Modify:**

1. **`packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`**

Add to `SUPPORTED_MODELS`:
```python
"avatar": [
    "omnihuman_v1_5",      # ByteDance OmniHuman - audio-driven animation
    "fabric_1_0",          # VEED Fabric - lipsync (image + audio)
    "fabric_1_0_text",     # VEED Fabric - text-to-speech avatar
    "kling_v2v_reference", # Kling - style-guided video generation
    "kling_v2v_edit",      # Kling - targeted video modifications
]
```

Add to `MODEL_RECOMMENDATIONS`:
```python
"avatar": {
    "quality": "omnihuman_v1_5",
    "speed": "fabric_1_0",
    "text_to_avatar": "fabric_1_0_text",
    "video_editing": "kling_v2v_edit",
    "style_transfer": "kling_v2v_reference",
}
```

Add to `COST_ESTIMATES`:
```python
"avatar": {
    "omnihuman_v1_5": 0.16,    # per second
    "fabric_1_0": 0.15,        # 720p per second
    "fabric_1_0_text": 0.15,   # 720p per second
    "kling_v2v_reference": 0.10,
    "kling_v2v_edit": 0.10,
}
```

Add to `PROCESSING_TIME_ESTIMATES`:
```python
"avatar": {
    "omnihuman_v1_5": 60,      # seconds
    "fabric_1_0": 45,
    "fabric_1_0_text": 45,
    "kling_v2v_reference": 30,
    "kling_v2v_edit": 30,
}
```

2. **`packages/core/ai_content_pipeline/ai_content_pipeline/models/avatar.py`**

Update to include FAL avatar models:
```python
from packages.providers.fal.avatar_generation.fal_avatar.generator import FALAvatarGenerator

class UnifiedAvatarGenerator(BaseContentModel):
    def __init__(self):
        super().__init__("avatar")
        self.fal_generator = FALAvatarGenerator()
        self.replicate_generator = ReplicateMultiTalkGenerator()

    def generate(self, input_data=None, model="omnihuman_v1_5", **kwargs) -> ModelResult:
        if model in self.fal_generator.list_models():
            return self._generate_with_fal(model, **kwargs)
        elif model == "multitalk":
            return self._generate_with_replicate(**kwargs)
```

3. **`packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py`**

Ensure avatar step type is properly handled in pipeline execution.

---

### Subtask 4: Add CLI Commands (30-45 min)

**Goal:** Add CLI support for avatar generation

**File to Modify:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

**Add Commands:**
```python
@cli.command()
@click.option("--image", required=True, help="Image URL or local path")
@click.option("--audio", help="Audio URL or local path")
@click.option("--text", help="Text for TTS avatar")
@click.option("--video", help="Video URL for video-to-video")
@click.option("--model", default="omnihuman_v1_5", help="Avatar model to use")
@click.option("--resolution", default="720p", help="Output resolution")
@click.option("--output", help="Output directory")
def generate_avatar(image, audio, text, video, model, resolution, output):
    """Generate avatar video from image + audio/text or transform video"""
```

**Usage Examples:**
```bash
# Audio-driven avatar (OmniHuman)
aicp generate-avatar --image face.jpg --audio speech.mp3 --model omnihuman_v1_5

# Lipsync with audio (Fabric)
aicp generate-avatar --image face.jpg --audio speech.mp3 --model fabric_1_0

# Text-to-speech avatar (Fabric Text)
aicp generate-avatar --image face.jpg --text "Hello world" --model fabric_1_0_text

# Video style transfer (Kling Reference)
aicp generate-avatar --video source.mp4 --model kling_v2v_reference --prompt "cinematic style"

# Video editing (Kling Edit)
aicp generate-avatar --video source.mp4 --model kling_v2v_edit --prompt "change background to beach"
```

---

### Subtask 5: Add YAML Pipeline Support (30-45 min)

**Goal:** Enable avatar steps in YAML pipeline configurations

**File to Modify:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py`

**YAML Configuration Example:**
```yaml
# input/pipelines/avatar_example.yaml
name: "Avatar Generation Pipeline"
description: "Generate talking avatar from image and text"

steps:
  - name: "generate_avatar"
    type: "avatar"
    model: "fabric_1_0_text"
    params:
      image_url: "https://example.com/face.jpg"
      text: "Hello, this is a demonstration of the avatar pipeline."
      resolution: "720p"
      voice_description: "Professional female voice"
    output: "avatar_video"

  - name: "upscale_video"
    type: "video_processing"
    model: "topaz"
    params:
      video_url: "{{generate_avatar.output}}"
      scale: 2
```

**Multi-step Pipeline Example:**
```yaml
# input/pipelines/avatar_from_script.yaml
name: "Script to Avatar Video"
description: "Generate image, then create avatar from text"

steps:
  - name: "generate_portrait"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "Professional headshot of a businesswoman, neutral background"
    output: "portrait_image"

  - name: "create_avatar"
    type: "avatar"
    model: "omnihuman_v1_5"
    params:
      image_url: "{{generate_portrait.output}}"
      audio_url: "https://example.com/narration.mp3"
      resolution: "1080p"
    output: "avatar_video"
```

---

### Subtask 6: Write Unit Tests (45 min - 1 hour)

**Goal:** Create comprehensive tests for avatar functionality

**Files to Create:**
```
tests/
├── test_avatar_models.py        # Model class tests
├── test_avatar_generator.py     # Generator tests
└── test_avatar_pipeline.py      # Pipeline integration tests
```

**`tests/test_avatar_models.py`:**
```python
import pytest
from packages.providers.fal.avatar_generation.fal_avatar.models import (
    OmniHumanModel, FabricModel, FabricTextModel,
    KlingReferenceModel, KlingEditModel
)

class TestOmniHumanModel:
    def test_model_initialization(self):
        model = OmniHumanModel()
        assert model.model_name == "omnihuman_v1_5"
        assert model.endpoint == "fal-ai/bytedance/omnihuman/v1.5"

    def test_cost_estimation(self):
        model = OmniHumanModel()
        cost = model.estimate_cost(duration=10)
        assert cost == 1.60  # $0.16 * 10 seconds

    def test_parameter_validation_missing_image(self):
        model = OmniHumanModel()
        with pytest.raises(ValueError):
            model.validate_parameters(audio_url="test.mp3")

class TestFabricModel:
    def test_resolution_pricing(self):
        model = FabricModel()
        cost_480p = model.estimate_cost(duration=10, resolution="480p")
        cost_720p = model.estimate_cost(duration=10, resolution="720p")
        assert cost_480p == 0.80   # $0.08 * 10
        assert cost_720p == 1.50   # $0.15 * 10
```

**`tests/test_avatar_generator.py`:**
```python
import pytest
from packages.providers.fal.avatar_generation.fal_avatar.generator import FALAvatarGenerator

class TestFALAvatarGenerator:
    def test_list_models(self):
        generator = FALAvatarGenerator()
        models = generator.list_models()
        assert "omnihuman_v1_5" in models
        assert "fabric_1_0" in models
        assert len(models) == 5

    def test_get_model_info(self):
        generator = FALAvatarGenerator()
        info = generator.get_model_info("omnihuman_v1_5")
        assert "endpoint" in info
        assert "pricing" in info
```

---

### Subtask 7: Update Documentation (30 min)

**Goal:** Update README and add usage examples

**Files to Modify:**
- `README.md` - Add avatar models to supported models list
- `CLAUDE.md` - Add avatar commands to common commands section

**New Documentation:**
```markdown
### 📦 Avatar Generation (5 models)
- **OmniHuman v1.5** - Audio-driven human animation ($0.16/sec)
- **Fabric 1.0** - Lipsync video from image + audio ($0.08-0.15/sec)
- **Fabric 1.0 Text** - Text-to-speech avatar videos ($0.08-0.15/sec)
- **Kling V2V Reference** - Style-guided video generation ($0.10/sec)
- **Kling V2V Edit** - Targeted video modifications ($0.10/sec)
```

---

## File Path Summary

| Category | File Path | Action |
|----------|-----------|--------|
| **New Models** | `packages/providers/fal/avatar-generation/fal_avatar/models/omnihuman.py` | Create |
| **New Models** | `packages/providers/fal/avatar-generation/fal_avatar/models/fabric.py` | Create |
| **New Models** | `packages/providers/fal/avatar-generation/fal_avatar/models/kling_v2v.py` | Create |
| **New Models** | `packages/providers/fal/avatar-generation/fal_avatar/models/base.py` | Create |
| **Generator** | `packages/providers/fal/avatar-generation/fal_avatar/generator.py` | Create |
| **Constants** | `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py` | Create |
| **Core Constants** | `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py` | Modify |
| **Core Avatar** | `packages/core/ai_content_pipeline/ai_content_pipeline/models/avatar.py` | Modify |
| **Pipeline** | `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py` | Modify |
| **CLI** | `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Modify |
| **Tests** | `tests/test_avatar_models.py` | Create |
| **Tests** | `tests/test_avatar_generator.py` | Create |
| **Docs** | `README.md` | Modify |
| **Docs** | `CLAUDE.md` | Modify |

---

## Input Types Summary

| Model | Image | Audio | Video | Text |
|-------|-------|-------|-------|------|
| OmniHuman v1.5 | ✅ Required | ✅ Required | ❌ | ⚪ Optional prompt |
| Fabric 1.0 | ✅ Required | ✅ Required | ❌ | ❌ |
| Fabric 1.0 Text | ✅ Required | ❌ | ❌ | ✅ Required |
| Kling V2V Reference | ⚪ Optional | ⚪ Optional | ✅ Required | ✅ Required prompt |
| Kling V2V Edit | ❌ | ❌ | ✅ Required | ✅ Required prompt |

---

## Dependencies

No new dependencies required - uses existing:
- `fal-client` (already installed)
- `click` (already installed)
- `pydantic` (already installed)

---

## References

- [OmniHuman v1.5 API](https://fal.ai/models/fal-ai/bytedance/omnihuman/v1.5/api)
- [VEED Fabric 1.0 API](https://fal.ai/models/veed/fabric-1.0/api)
- [VEED Fabric 1.0 Text API](https://fal.ai/models/veed/fabric-1.0/text/api)
- [Kling O1 Developer Guide](https://fal.ai/learn/devs/kling-o1-developer-guide)
- [Kling V2V Reference API](https://fal.ai/models/fal-ai/kling-video/o1/standard/video-to-video/reference/api)
- [Kling V2V Edit API](https://fal.ai/models/fal-ai/kling-video/o1/standard/video-to-video/edit/api)
