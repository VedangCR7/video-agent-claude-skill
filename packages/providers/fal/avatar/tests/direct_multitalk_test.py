#!/usr/bin/env python3
"""
Direct MultiTalk Test - Exact Replicate Example

This script uses the exact same code structure as the Replicate example:
output = replicate.run("zsxkib/multitalk:...", input={...})

⚠️ WARNING: This makes actual API calls and costs money!
"""

import replicate
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports (if needed)
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()


def test_direct_multitalk():
    """Test MultiTalk using direct replicate.run() call"""
    print("🎬 Direct MultiTalk Test - Exact Replicate Example")
    print("=" * 60)

    # Check API token
    if not os.getenv("REPLICATE_API_TOKEN"):
        print("❌ REPLICATE_API_TOKEN not found in environment")
        print("💡 Set your token in .env file or environment variable")
        return False

    print("⚠️ WARNING: This will make actual API calls and cost money!")
    print("💰 Estimated cost: $0.50-2.00")

    confirm = input("\nProceed with real generation? (y/N): ")
    if confirm.lower() != "y":
        print("❌ Test cancelled")
        return False

    try:
        print("\n🚀 Running exact Replicate example...")

        # Exact code from the example you provided
        output = replicate.run(
            "zsxkib/multitalk:0bd2390c40618c910ffc345b36c8fd218fd8fa59c9124aa641fea443fa203b44",
            input={
                "image": "https://replicate.delivery/pbxt/NHF6Y7EeJGK6pp4rDODjJS8m0nk9rj32iuaVQs8IfOl7S4vJ/multi1.png",
                "turbo": True,
                "prompt": "In a casual, intimate setting, a man and a woman are engaged in a heartfelt conversation inside a car. The man, sporting a denim jacket over a blue shirt, sits attentively with a seatbelt fastened, his gaze fixed on the woman beside him. The woman, wearing a black tank top and a denim jacket draped over her shoulders, smiles warmly, her eyes reflecting genuine interest and connection. The car's interior, with its beige seats and simple design, provides a backdrop that emphasizes their interaction. The scene captures a moment of shared understanding and connection, set against the soft, diffused light of an overcast day. A medium shot from a slightly angled perspective, focusing on their expressions and body language",
                "num_frames": 81,
                "first_audio": "https://replicate.delivery/pbxt/NHF6XifveoBBNUVcYdrkqkiLqq2vDI7g322dYXadTtF4BFZ9/1.WAV",
                "second_audio": "https://replicate.delivery/pbxt/NHF6Y526MirDQ9byxeuIxcnrnW5CeISX11fWxr78FP9d3gut/2.WAV",
                "sampling_steps": 10,
            },
        )

        print("\n✅ Generation completed!")
        print(f"📤 Output: {output}")

        # Download the video if it's a URL
        if isinstance(output, str) and output.startswith("http"):
            print("\n📥 Downloading video...")

            import requests

            response = requests.get(output)
            response.raise_for_status()

            output_path = "output/direct_multitalk_test.mp4"
            os.makedirs("output", exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(response.content)

            file_size = os.path.getsize(output_path)
            print(
                f"✅ Video downloaded: {output_path} ({file_size / (1024 * 1024):.2f} MB)"
            )

        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def main():
    """Main function"""
    print("🗣️ Direct MultiTalk Test")
    print("Using exact replicate.run() call from official example")
    print("=" * 70)

    success = test_direct_multitalk()

    if success:
        print("\n🎉 Direct test completed successfully!")
        print("📁 Check output/direct_multitalk_test.mp4 for the result")
    else:
        print("\n❌ Direct test failed")

    print("\n📋 Test used:")
    print("   • Model: zsxkib/multitalk (latest version)")
    print("   • Real image and audio assets from Replicate")
    print("   • Exact parameters from official example")
    print("   • Direct replicate.run() call (no wrapper)")


if __name__ == "__main__":
    main()
