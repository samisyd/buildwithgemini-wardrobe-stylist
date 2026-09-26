"""Video generation tool for WardrobeAI agent using gemini-omni-flash-preview."""

import base64
from typing import Any, Dict
import uuid

from google.adk.tools import ToolContext
from google.cloud import storage
import google.genai as genai
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-04-7202d2aeaa87"
STORAGE_BUCKET_NAME = "wardrobestylist-qwiklabs-gcp-04-7202d2aeaa87"
MODEL_NAME = "gemini-omni-flash-preview"
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


async def generate_wardrobe_item_video(
    prompt: str,
    tool_context: ToolContext,
    aspect_ratio: str = "16:9",
    duration: str = "4s",
) -> Dict[str, Any]:
    """Generate a short video showcase for an apparel or wardrobe item using gemini-omni-flash-preview.

    Args:
        prompt: Detailed description of the apparel piece or fashion showcase to animate
                (e.g., 'A model turning in a studio wearing a classic camel wool trench coat, cinematic lighting'
                 or 'Close up of a silk scarf fluttering gracefully in a gentle breeze').
        tool_context: The ADK tool execution context for saving artifacts.
        aspect_ratio: Aspect ratio for the video ('16:9' or '9:16'). Default is '16:9'.
        duration: Duration between '3s' and '10s' (e.g. '4s'). Default is '4s'.

    Returns:
        A dictionary with the public HTTPS URL of the uploaded video, artifact metadata, and filename.
    """
    client = get_genai_client()

    # Omni model video generation via Interactions API
    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=[
            {
                "type": "user_input",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
        response_format=[
            {
                "type": "video",
                "delivery": "inline",
                "aspect_ratio": aspect_ratio,
                "duration": duration,
            }
        ],
        background=False,
        store=False,
    )

    video_bytes = None
    mime_type = "video/mp4"

    # Extract video data from interaction steps
    for step in getattr(interaction, "steps", []):
        if getattr(step, "type", None) == "model_output" and hasattr(step, "content"):
            for content in step.content:
                if getattr(content, "type", None) == "video":
                    raw_data = getattr(content, "data", None)
                    if raw_data:
                        if isinstance(raw_data, str):
                            video_bytes = base64.b64decode(raw_data)
                        elif isinstance(raw_data, (bytes, bytearray)):
                            video_bytes = bytes(raw_data)
                    mime_type = getattr(content, "mime_type", None) or "video/mp4"
                    break
        if video_bytes:
            break

    # Fallback to output_video helper if present
    if not video_bytes and hasattr(interaction, "output_video") and interaction.output_video:
        ov = interaction.output_video
        raw_data = getattr(ov, "data", None)
        if raw_data:
            if isinstance(raw_data, str):
                video_bytes = base64.b64decode(raw_data)
            elif isinstance(raw_data, (bytes, bytearray)):
                video_bytes = bytes(raw_data)
        mime_type = getattr(ov, "mime_type", None) or mime_type

    if not video_bytes:
        return {"error": "Failed to extract video bytes from gemini-omni-flash-preview response."}

    # Generate unique filename for artifact and GCS
    ext = "mp4" if "mp4" in mime_type else "webm"
    filename = f"wardrobe_video_{uuid.uuid4().hex[:8]}.{ext}"

    # (1) Save video artifact with tool_context.save_artifact so it shows in Playground's Artifacts panel
    artifact_part = types.Part(
        inline_data=types.Blob(
            mime_type=mime_type,
            data=video_bytes,
        )
    )
    artifact_version = None
    try:
        artifact_version = await tool_context.save_artifact(filename, artifact_part)
    except Exception as e:
        # Graceful handling if artifact service is not bound in certain environments
        pass

    # (2) Upload the same video bytes to the public Cloud Storage bucket
    storage_client = get_storage_client()
    bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{STORAGE_BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "filename": filename,
        "artifact_version": artifact_version,
        "video_url": public_url,
        "mime_type": mime_type,
    }
