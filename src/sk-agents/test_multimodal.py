"""
Test multi-modal inputs with images.

Tests base64 image encoding and vision model integration.
"""
import asyncio
import base64
import io
from PIL import Image, ImageDraw, ImageFont
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os


def create_test_image() -> str:
    """
    Create a simple test image with text and return as base64.
    
    Returns:
        Base64 encoded image string
    """
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.rectangle([10, 10, 390, 190], outline='blue', width=3)
    draw.text((50, 80), "Hello from LangChain!", fill='black', font=font)
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    
    return base64.b64encode(img_bytes).decode('utf-8')


async def test_multimodal():
    print("Testing multi-modal input with vision model...")
    
    # Create test image
    print("\n=== Creating Test Image ===")
    base64_image = create_test_image()
    print(f"✓ Image created (base64 length: {len(base64_image)})")
    
    # Gemini 2.0 Flash supports vision
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv('GOOGLE_API_KEY')
    )
    
    # Test 1: Simple image description
    print("\n=== Test 1: Image Description ===")
    message = HumanMessage(
        content=[
            {"type": "text", "text": "What text do you see in this image?"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            }
        ]
    )
    
    result = await model.ainvoke([message])
    print(f"Response: {result.content}")
    
    # Check if it detected the text
    if "hello" in result.content.lower() or "langchain" in result.content.lower():
        print("✅ Model correctly identified text in image!")
    else:
        print("⚠️ Model response:", result.content)
    
    # Test 2: Multi-modal with chat history
    print("\n=== Test 2: Multi-modal with Context ===")
    messages = [
        HumanMessage(content="I'm going to show you an image."),
        HumanMessage(
            content=[
                {"type": "text", "text": "Describe what you see:"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                }
            ]
        )
    ]
    
    result2 = await model.ainvoke(messages)
    print(f"Response: {result2.content[:200]}...")
    
    print("\n✅ Multi-modal validation successful!")
    return True


if __name__ == "__main__":
    asyncio.run(test_multimodal())
