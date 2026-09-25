"""Seed script to populate Firestore with initial wardrobe items."""

import os
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-7202d2aeaa87"
COLLECTION_NAME = "wardrobe_items"

SAMPLE_ITEMS = [
    {
        "id": "item-001",
        "name": "Classic White Linen Shirt",
        "category": "tops",
        "color": "white",
        "brand": "Uniqlo",
        "size": "M",
        "material": "100% French Linen",
        "season": ["spring", "summer"],
        "occasion": ["casual", "smart casual"],
        "price": 39.90,
        "tags": ["minimalist", "breathable", "classic"],
    },
    {
        "id": "item-002",
        "name": "Navy Tailored Wool Blazer",
        "category": "outerwear",
        "color": "navy",
        "brand": "Suitsupply",
        "size": "38R",
        "material": "Italian Wool",
        "season": ["fall", "winter", "spring"],
        "occasion": ["formal", "business", "smart casual"],
        "price": 399.00,
        "tags": ["tailored", "elegant", "formal"],
    },
    {
        "id": "item-003",
        "name": "Slim-Fit Selvedge Denim",
        "category": "bottoms",
        "color": "indigo",
        "brand": "APC",
        "size": "32x32",
        "material": "100% Cotton Denim",
        "season": ["all-season"],
        "occasion": ["casual", "smart casual", "streetwear"],
        "price": 220.00,
        "tags": ["selvedge", "durable", "streetwear"],
    },
    {
        "id": "item-004",
        "name": "Oversized Cashmere Crewneck",
        "category": "tops",
        "color": "camel",
        "brand": "Everlane",
        "size": "M",
        "material": "100% Grade-A Cashmere",
        "season": ["fall", "winter"],
        "occasion": ["casual", "cozy", "smart casual"],
        "price": 170.00,
        "tags": ["soft", "warm", "minimalist"],
    },
    {
        "id": "item-005",
        "name": "Minimalist White Leather Sneakers",
        "category": "shoes",
        "color": "white",
        "brand": "Common Projects",
        "size": "42 EU",
        "material": "Italian Nappa Leather",
        "season": ["spring", "summer", "fall"],
        "occasion": ["casual", "smart casual", "streetwear"],
        "price": 425.00,
        "tags": ["iconic", "versatile", "clean"],
    },
]


def seed_database():
    print(f"Connecting to Firestore with project_id={PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    for item in SAMPLE_ITEMS:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"Seeded document: {doc_id} -> {item['name']}")

    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
