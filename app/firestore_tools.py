"""Firestore backend tools for WardrobeStylist agent."""

from typing import Any, Dict, List, Optional
import uuid
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-7202d2aeaa87"
COLLECTION_NAME = "wardrobe_items"

# Initialize Firestore client with hardcoded project ID
_db: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    """Return a singleton instance of the Firestore client."""
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def list_wardrobe_items(
    category: Optional[str] = None,
    season: Optional[str] = None,
    occasion: Optional[str] = None,
    color: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """List or search wardrobe items from Firestore with optional filtering.

    Args:
        category: Filter by item category (e.g., 'tops', 'bottoms', 'outerwear', 'shoes').
        season: Filter by suitable season (e.g., 'spring', 'summer', 'fall', 'winter', 'all-season').
        occasion: Filter by occasion (e.g., 'casual', 'formal', 'smart casual', 'streetwear', 'business').
        color: Filter by color (e.g., 'white', 'navy', 'camel', 'indigo').
        limit: Max number of items to retrieve (default: 20).

    Returns:
        A list of wardrobe item dictionaries containing item details.
    """
    db = get_db()
    docs = db.collection(COLLECTION_NAME).stream()

    items: List[Dict[str, Any]] = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # Apply in-memory filtering for flexible matching
        if category and data.get("category", "").lower() != category.lower():
            continue
        if color and data.get("color", "").lower() != color.lower():
            continue
        if season:
            item_seasons = [s.lower() for s in data.get("season", [])]
            if season.lower() not in item_seasons and "all-season" not in item_seasons:
                continue
        if occasion:
            item_occasions = [o.lower() for o in data.get("occasion", [])]
            if occasion.lower() not in item_occasions:
                continue

        items.append(data)
        if len(items) >= limit:
            break

    return items


def search_wardrobe_catalog(
    query: Optional[str] = None,
    category: Optional[str] = None,
    season: Optional[str] = None,
    occasion: Optional[str] = None,
    color: Optional[str] = None,
    max_price: Optional[float] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Search wardrobe items and catalog apparel with keyword and attribute filters.

    Args:
        query: Free-text search keyword to match item name, brand, material, or style tags (e.g. 'linen', 'sneakers', 'cashmere').
        category: Filter by item category ('tops', 'bottoms', 'outerwear', 'shoes', 'accessories').
        season: Filter by suitable season ('spring', 'summer', 'fall', 'winter', 'all-season').
        occasion: Filter by occasion ('casual', 'formal', 'smart casual', 'streetwear', 'business').
        color: Filter by color (e.g., 'white', 'navy', 'indigo', 'camel').
        max_price: Maximum price budget for the item.
        limit: Max number of items to return (default: 20).

    Returns:
        A list of matching wardrobe items with their complete specifications.
    """
    db = get_db()
    docs = db.collection(COLLECTION_NAME).stream()

    matches: List[Dict[str, Any]] = []
    q_lower = query.lower().strip() if query else None

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # Keyword matching across name, brand, material, and tags
        if q_lower:
            name_match = q_lower in data.get("name", "").lower()
            brand_match = q_lower in data.get("brand", "").lower()
            mat_match = q_lower in data.get("material", "").lower()
            tags_match = any(q_lower in tag.lower() for tag in data.get("tags", []))
            cat_match = q_lower in data.get("category", "").lower()
            if not (name_match or brand_match or mat_match or tags_match or cat_match):
                continue

        # Attribute filters
        if category and data.get("category", "").lower() != category.lower():
            continue
        if color and data.get("color", "").lower() != color.lower():
            continue
        if max_price is not None and data.get("price", 0.0) > max_price:
            continue
        if season:
            item_seasons = [s.lower() for s in data.get("season", [])]
            if season.lower() not in item_seasons and "all-season" not in item_seasons:
                continue
        if occasion:
            item_occasions = [o.lower() for o in data.get("occasion", [])]
            if occasion.lower() not in item_occasions:
                continue

        matches.append(data)
        if len(matches) >= limit:
            break

    return matches


def get_wardrobe_item(item_id: str) -> Dict[str, Any]:
    """Retrieve details for a specific wardrobe item by its unique ID.

    Args:
        item_id: The unique ID of the wardrobe item (e.g., 'item-001').

    Returns:
        The item details if found, or an error status dictionary.
    """
    db = get_db()
    doc_ref = db.collection(COLLECTION_NAME).document(item_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Item with ID '{item_id}' not found."}

    data = doc.to_dict()
    data["id"] = doc.id
    return data


def add_wardrobe_item(
    name: str,
    category: str,
    color: str,
    brand: Optional[str] = None,
    size: Optional[str] = None,
    material: Optional[str] = None,
    season: Optional[List[str]] = None,
    occasion: Optional[List[str]] = None,
    price: Optional[float] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add a new clothing piece or accessory to the wardrobe catalog.

    Args:
        name: Name or description of the apparel item (e.g. 'Cashmere Ribbed Beanie').
        category: Item category ('tops', 'bottoms', 'outerwear', 'shoes', 'accessories').
        color: Primary color of the garment.
        brand: Brand or designer name.
        size: Size (e.g., 'S', 'M', 'L', '32x32', '42 EU').
        material: Fabric composition (e.g., '100% Cotton', 'Merino Wool').
        season: List of seasons it's suitable for ('spring', 'summer', 'fall', 'winter', 'all-season').
        occasion: List of occasions ('casual', 'formal', 'smart casual', 'streetwear', 'business').
        price: Estimated or purchase price.
        tags: Style tags or descriptors (e.g. ['minimalist', 'oversized', 'vintage']).

    Returns:
        A dictionary confirming creation with the assigned item ID and details.
    """
    db = get_db()
    item_id = f"item-{uuid.uuid4().hex[:8]}"

    item_data = {
        "id": item_id,
        "name": name,
        "category": category,
        "color": color,
        "brand": brand or "Unknown",
        "size": size or "Standard",
        "material": material or "Unspecified",
        "season": season or ["all-season"],
        "occasion": occasion or ["casual"],
        "price": price or 0.0,
        "tags": tags or [],
    }

    db.collection(COLLECTION_NAME).document(item_id).set(item_data)
    return {"status": "success", "item": item_data}
