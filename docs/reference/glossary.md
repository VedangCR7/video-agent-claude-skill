# Glossary

Definitions of terms used throughout the AI Content Generation Suite documentation.

## A

### API Key
A secret authentication token used to access AI provider services. Each provider (FAL AI, Google, ElevenLabs) requires its own API key.

### Aspect Ratio
The proportional relationship between width and height of an image or video. Common ratios include:
- **1:1** - Square (Instagram posts)
- **16:9** - Widescreen landscape (YouTube, presentations)
- **9:16** - Portrait (Instagram Stories, TikTok)
- **4:3** - Traditional screen ratio

## B

### Batch Processing
Executing multiple similar operations together, often in parallel, for efficiency. Example: generating 10 images at once.

## C

### CLI (Command-Line Interface)
A text-based interface for interacting with the software. The package provides `ai-content-pipeline` and `aicp` commands.

### Cost Estimation
The process of calculating expected API costs before running operations. Helps avoid unexpected charges.

## D

### Diffusion Model
A type of AI model that generates images by gradually removing noise from a random starting point. Examples: FLUX, Stable Diffusion.

### Dry Run
Executing a pipeline configuration to validate it without actually calling APIs or generating content. No costs incurred.

## E

### Embedding
A numerical representation of data (text, images) that AI models use internally. Not directly visible to users.

### Endpoint
A specific URL or API path that handles a particular type of request. Each AI operation has its own endpoint.

## F

### FAL AI
A cloud AI platform providing access to multiple image and video generation models. Primary provider for this package.

### FLUX
A family of text-to-image models known for high-quality output:
- **FLUX.1 Dev** - High-quality, 12B parameters
- **FLUX.1 Schnell** - Fast generation

## G

### Generation
The process of creating new content (images, videos, audio) using AI models.

### Gemini
Google's multimodal AI model family used for image understanding and analysis.

### Guidance Scale
A parameter controlling how closely the generated image follows the text prompt. Higher values = stricter adherence.

## H

### Hailuo
MiniMax's video generation model, known for budget-friendly pricing.

## I

### Image-to-Image
Transformation of an existing image based on a text prompt. Used for editing, style transfer, or enhancement.

### Image-to-Video
Converting a static image into an animated video clip.

### Imagen
Google's text-to-image model known for photorealistic output.

### Inference
The process of running an AI model to generate output from input. Each API call involves inference.

### Input Variable
A placeholder in pipeline configurations (like `{{input}}`) that gets replaced with actual values at runtime.

## K

### Kling
A video generation model by Kuaishou, available in multiple versions (v2.1, v2.6 Pro).

## L

### Latency
The time delay between sending a request and receiving a response. Varies by model and provider.

### LLM (Large Language Model)
AI models trained on text data, used for understanding prompts and generating descriptions.

## M

### Mock Mode
A testing mode that simulates API calls without actually making them. Useful for validating configurations without cost.

### Model
An AI system trained to perform specific tasks. Different models have different capabilities, costs, and output quality.

### Multimodal
AI systems that can process multiple types of input (text, images, audio, video).

## N

### Negative Prompt
Text describing what you don't want in the generated output. Supported by some models.

## O

### Output Directory
The folder where generated files are saved. Default is `output/` in the current directory.

## P

### Parallel Execution
Running multiple operations simultaneously to reduce total processing time.

### Pipeline
A sequence of AI operations defined in a YAML configuration file. Steps can be chained together.

### Prompt
Text instructions given to an AI model describing the desired output.

### Provider
A company or service offering AI model access via API. Examples: FAL AI, Google, ElevenLabs.

## R

### Rate Limit
Maximum number of API requests allowed within a time period. Exceeding causes temporary blocks.

### Resolution
The dimensions of an image or video, measured in pixels (e.g., 1024x1024, 1920x1080).

## S

### Sampling Steps
The number of iterations a diffusion model uses during generation. More steps = higher quality but slower.

### Seed
A number that initializes the random number generator. Using the same seed produces reproducible results.

### Sora
OpenAI's video generation model, available in standard and Pro versions.

### Step
A single operation within a pipeline. Each step has a type, model, and parameters.

### Step Type
The category of operation a step performs:
- `text_to_image`
- `image_to_image`
- `image_to_video`
- `text_to_video`
- `text_to_speech`
- `analyze_image`
- `parallel_group`

## T

### Text-to-Image
Generating an image from a text description.

### Text-to-Speech (TTS)
Converting written text into spoken audio.

### Text-to-Video
Generating a video directly from a text description.

### Token
A unit of text processed by language models. Roughly 4 characters or 0.75 words on average.

## U

### Upscaling
Increasing the resolution of an image or video while maintaining or improving quality.

## V

### Variable Interpolation
The process of replacing placeholders (like `{{input}}`) with actual values in pipeline configurations.

### Veo
Google's video generation model, available through Vertex AI.

### Video-to-Video
Processing an existing video to modify, enhance, or add effects.

### Voice
A specific speaker identity used in text-to-speech generation. ElevenLabs offers 20+ voice options.

## W

### Wan
A video generation model supporting multi-shot sequences and audio input.

### Worker
A processing unit handling operations in parallel execution. More workers = more concurrent operations.

## Y

### YAML
A human-readable data format used for pipeline configuration files. Files end with `.yaml` or `.yml`.

---

## Common Abbreviations

| Abbreviation | Full Term |
|--------------|-----------|
| API | Application Programming Interface |
| CLI | Command-Line Interface |
| GPU | Graphics Processing Unit |
| I2I | Image-to-Image |
| I2V | Image-to-Video |
| JSON | JavaScript Object Notation |
| LLM | Large Language Model |
| OCR | Optical Character Recognition |
| PNG | Portable Network Graphics |
| SDK | Software Development Kit |
| T2I | Text-to-Image |
| T2S | Text-to-Speech |
| T2V | Text-to-Video |
| TTS | Text-to-Speech |
| YAML | YAML Ain't Markup Language |

---

[Back to Documentation Index](../index.md)
