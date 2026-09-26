"""Image generation tool for WardrobeStylist agent using gemini-3.1-flash-lite-image."""

from typing import Any, Dict
import uuid
from google.adk.tools import ToolContext
from google.cloud import storage
import google.genai as genai
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-04-7202d2aeaa87"
STORAGE_BUCKET_NAME = "wardrobestylist-qwiklabs-gcp-04-7202d2aeaa87"
MODEL_NAME = "gemini-3.1-flash-lite-image"
LOCATION = "global"

_genai_client = None
_storage_client = None


def get_genai_client() -> genai.Client:
    """Return a singleton instance of the GenAI client configured for Vertex AI."""
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )
    return _genai_client


def get_storage_client() -> storage.Client:
    """Return a singleton instance of the Cloud Storage client."""
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


async def generate_wardrobe_item_image(
    prompt: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generate a photo or visual rendering of a wardrobe piece, apparel item, or outfit moodboard.

    Args:
        prompt: Detailed description of the clothing item or outfit to visually render
                (e.g., 'Classic white linen button-down shirt on wooden hanger, minimalist studio lighting').
        tool_context: The ADK tool execution context for saving artifacts.

    Returns:
        A dictionary with the public HTTPS URL of the uploaded image and artifact details.
    """
    client = get_genai_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"

    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break

    if not image_bytes:
        return {"error": "Failed to generate image bytes from model response."}

    # Generate a unique filename
    ext = "jpg" if "jpeg" in mime_type else "png"
    filename = f"wardrobe_{uuid.uuid4().hex[:8]}.{ext}"

    # (1) Save artifact for Playground's Artifacts panel
    artifact_part = types.Part(
        inline_data=types.Blob(
            mime_type=mime_type,
            data=image_bytes,
        )
    )
    version = None
    try:
        version = await tool_context.save_artifact(filename, artifact_part)
    except Exception as e:
        # Artifact service might not be initialized in non-adk-web standalone runs
        pass

    # (2) Upload image bytes to public Cloud Storage bucket
    storage_client = get_storage_client()
    bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "filename": filename,
        "artifact_version": version,
        "image_url": public_url,
    }
