# Model Fashion Week Workflow

## Overview

This workflow generates a fashion week video story using:
1. **Step 1:** Generate 3 styled images using Nano Banana Pro Edit
2. **Step 2:** Create videos from each image using the Image-to-Video CLI

## Source Image

```
c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\input\images\character\miranda.jpg
```

---

## Step 1: Generate 3 Fashion Week Images

### Using Nano Banana Pro Edit Model

The Nano Banana Pro Edit model supports multi-image editing with resolution control.

**Model Features:**
- Aspect ratios: auto, 21:9, 16:9, 3:2, 4:3, 5:4, 1:1, 4:5, 3:4, 2:3, 9:16
- Resolutions: 1K, 2K, 4K
- Pricing: $0.015/image (1K/2K), $0.030/image (4K)

### Python Script: `generate_fashion_images.py`

Create this file in `output/` directory:

```python
"""
Generate 3 fashion week styled images using Nano Banana Pro Edit.
"""

import sys
from pathlib import Path

# Add package to path
package_path = Path(__file__).parent.parent / "packages" / "providers" / "fal" / "image-to-image"
sys.path.insert(0, str(package_path))

from fal_image_to_image.generator import FALImageToImageGenerator

# Configuration
INPUT_IMAGE = Path(__file__).parent.parent / "input" / "images" / "character" / "miranda.jpg"
OUTPUT_DIR = Path(__file__).parent

# Fashion week prompts for 3 different looks
FASHION_PROMPTS = [
    {
        "name": "runway_entrance",
        "prompt": """Transform into a high fashion model walking the runway at Milan Fashion Week.
        Elegant designer gown with flowing fabric, dramatic lighting from above,
        professional runway setting with blurred audience in background,
        confident powerful stride, editorial fashion photography style.""",
        "aspect_ratio": "9:16"  # Portrait for runway
    },
    {
        "name": "backstage_glamour",
        "prompt": """Transform into a supermodel in a backstage fashion week setting.
        Luxury makeup station with Hollywood lights, designer outfit with bold colors,
        getting final touches before the show, candid glamorous moment,
        backstage energy and excitement, fashion documentary style.""",
        "aspect_ratio": "16:9"  # Landscape for backstage scene
    },
    {
        "name": "front_row_vip",
        "prompt": """Transform into a celebrity VIP sitting front row at Paris Fashion Week.
        Sophisticated haute couture outfit, front row seating with other fashionistas,
        photographers flashing cameras, exclusive luxury atmosphere,
        poised elegant pose, paparazzi style photography.""",
        "aspect_ratio": "16:9"  # Landscape for crowd scene
    }
]


def main():
    """Generate 3 fashion week images."""
    print("=" * 60)
    print("Fashion Week Image Generation")
    print("Using Nano Banana Pro Edit Model")
    print("=" * 60)

    # Check input image exists
    if not INPUT_IMAGE.exists():
        print(f"Error: Input image not found: {INPUT_IMAGE}")
        return

    print(f"\nInput image: {INPUT_IMAGE}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Initialize generator
    generator = FALImageToImageGenerator()

    # Generate each fashion look
    results = []
    for i, look in enumerate(FASHION_PROMPTS, 1):
        print(f"\n{'='*40}")
        print(f"Look {i}/3: {look['name']}")
        print(f"{'='*40}")
        print(f"Prompt: {look['prompt'][:100]}...")
        print(f"Aspect ratio: {look['aspect_ratio']}")

        result = generator.modify_local_image(
            prompt=look["prompt"],
            image_path=str(INPUT_IMAGE),
            model="nano_banana_pro_edit",
            output_dir=str(OUTPUT_DIR),
            aspect_ratio=look["aspect_ratio"],
            resolution="2K",
            num_images=1
        )

        if result.get("success"):
            print(f"Success! Output: {result.get('image_path')}")
            results.append({
                "name": look["name"],
                "path": result.get("image_path"),
                "cost": result.get("cost_estimate", 0.015)
            })
        else:
            print(f"Failed: {result.get('error')}")
            results.append({"name": look["name"], "error": result.get("error")})

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    successful = [r for r in results if "path" in r]
    print(f"Generated: {len(successful)}/3 images")
    total_cost = sum(r.get("cost", 0) for r in successful)
    print(f"Total cost: ${total_cost:.3f}")

    print("\nGenerated images:")
    for r in successful:
        print(f"  - {r['name']}: {r['path']}")

    # Save paths for video generation
    if successful:
        paths_file = OUTPUT_DIR / "fashion_images.txt"
        with open(paths_file, "w") as f:
            for r in successful:
                f.write(f"{r['path']}\n")
        print(f"\nImage paths saved to: {paths_file}")


if __name__ == "__main__":
    main()
```

### Run Step 1

```bash
cd c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai
python output/generate_fashion_images.py
```

### Expected Output

```
Fashion Week Image Generation
Using Nano Banana Pro Edit Model
============================================================

Look 1/3: runway_entrance
Prompt: Transform into a high fashion model...
Aspect ratio: 9:16
Success! Output: output/modified_image_xxx.png

Look 2/3: backstage_glamour
...

Look 3/3: front_row_vip
...

SUMMARY
============================================================
Generated: 3/3 images
Total cost: $0.045

Generated images:
  - runway_entrance: output/modified_image_xxx.png
  - backstage_glamour: output/modified_image_xxx.png
  - front_row_vip: output/modified_image_xxx.png
```

---

## Step 2: Generate Fashion Week Videos (CLI)

Use the generated images to create fashion week videos using the Image-to-Video CLI.

### Video Prompts

| Image | Model | Video Prompt |
|-------|-------|--------------|
| runway_entrance | kling_2_6_pro | Model walks confidently down the runway, fabric flows elegantly, camera flashes, crowd watches in awe |
| backstage_glamour | kling_2_6_pro | Model receives final makeup touches, turns head, smiles at camera, backstage bustle around |
| front_row_vip | kling_2_6_pro | Celebrity model poses for photographers, slight smile, camera flashes illuminate the scene |

### CLI Commands

Navigate to the image-to-video package:

```bash
cd c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\packages\providers\fal\image-to-video
```

#### Video 1: Runway Entrance

```bash
python -m fal_image_to_video.cli generate ^
  --image "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\fashion_runway_entrance.png" ^
  --model kling_2_6_pro ^
  --prompt "The fashion model walks confidently down the Milan Fashion Week runway. Her elegant designer gown flows beautifully with each step. Camera flashes illuminate the scene as the captivated audience watches. She reaches the end of the runway, strikes a powerful pose, then turns gracefully to walk back." ^
  --duration 5 ^
  --output "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output" ^
  --negative-prompt "blur, distortion, low quality, amateur, shaky"
```

#### Video 2: Backstage Glamour

```bash
python -m fal_image_to_video.cli generate ^
  --image "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\fashion_backstage_glamour.png" ^
  --model kling_2_6_pro ^
  --prompt "Behind the scenes at Fashion Week. A makeup artist applies final touches to the supermodel. She turns her head slightly, checking her reflection. A smile spreads across her face as she's called to the runway. The bustling backstage energy surrounds her." ^
  --duration 5 ^
  --output "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output" ^
  --negative-prompt "blur, distortion, low quality, amateur"
```

#### Video 3: Front Row VIP

```bash
python -m fal_image_to_video.cli generate ^
  --image "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\fashion_front_row_vip.png" ^
  --model kling_2_6_pro ^
  --prompt "A celebrity sits front row at Paris Fashion Week. She notices the photographers, offers a subtle sophisticated smile. Camera flashes create a strobe effect. She turns to admire the runway show, clapping elegantly as a model passes by." ^
  --duration 5 ^
  --output "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output" ^
  --negative-prompt "blur, distortion, low quality, shaky camera"
```

### Alternative: Batch Script

Create `generate_fashion_videos.bat` in the output folder:

```batch
@echo off
echo ========================================
echo Fashion Week Video Generation
echo ========================================

cd /d c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\packages\providers\fal\image-to-video

echo.
echo Generating Video 1: Runway Entrance...
python -m fal_image_to_video.cli generate ^
  --image "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\fashion_runway_entrance.png" ^
  --model kling_2_6_pro ^
  --prompt "The fashion model walks confidently down the Milan Fashion Week runway. Her elegant designer gown flows beautifully with each step. Camera flashes illuminate the scene." ^
  --duration 5 ^
  --output "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output"

echo.
echo Generating Video 2: Backstage Glamour...
python -m fal_image_to_video.cli generate ^
  --image "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\fashion_backstage_glamour.png" ^
  --model kling_2_6_pro ^
  --prompt "Behind the scenes at Fashion Week. A makeup artist applies final touches. She turns, smiles, ready for the runway." ^
  --duration 5 ^
  --output "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output"

echo.
echo Generating Video 3: Front Row VIP...
python -m fal_image_to_video.cli generate ^
  --image "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\fashion_front_row_vip.png" ^
  --model kling_2_6_pro ^
  --prompt "A celebrity sits front row at Paris Fashion Week. Camera flashes as she smiles elegantly for photographers." ^
  --duration 5 ^
  --output "c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output"

echo.
echo ========================================
echo All videos generated!
echo ========================================
pause
```

---

## Cost Estimate

| Step | Model | Items | Cost per Item | Total |
|------|-------|-------|---------------|-------|
| Step 1 | Nano Banana Pro Edit (2K) | 3 images | $0.015 | $0.045 |
| Step 2 | Kling v2.6 Pro | 3 videos (5s each) | $0.50 | $1.50 |
| **Total** | | | | **$1.545** |

---

## Output Files

After running both steps, you should have:

### Images (Step 1)
- `output/fashion_runway_entrance.png`
- `output/fashion_backstage_glamour.png`
- `output/fashion_front_row_vip.png`

### Videos (Step 2)
- `output/kling_2_6_pro_video_[timestamp]_runway.mp4`
- `output/kling_2_6_pro_video_[timestamp]_backstage.mp4`
- `output/kling_2_6_pro_video_[timestamp]_frontrow.mp4`

---

## Quick Reference: CLI Commands

```bash
# List available video models
python -m fal_image_to_video.cli list-models

# Get model info
python -m fal_image_to_video.cli model-info kling_2_6_pro

# Generate video from image
python -m fal_image_to_video.cli generate \
  --image <path> \
  --model <model_name> \
  --prompt "<text>" \
  --duration <seconds> \
  --output <directory>
```

---

## Notes

1. **Image Generation**: Nano Banana Pro Edit preserves the character likeness while transforming the scene
2. **Video Model**: Kling v2.6 Pro chosen for high-quality motion and professional results
3. **Duration**: 5 seconds per video provides good motion without excessive cost
4. **Aspect Ratio**: Videos maintain source image aspect ratio

## Alternative Video Models

| Model | Price/sec | Best For |
|-------|-----------|----------|
| kling_2_6_pro | $0.10 | High quality, frame interpolation |
| kling_2_1 | $0.05 | Budget option, good quality |
| veo_3_1_fast | $0.10 | Fast processing, audio generation |
| sora_2_pro | $0.30 | Premium quality, 1080p |
