#!/usr/bin/env python3
"""
Test script to verify API endpoints
"""
import requests
import json
import sys

def test_api():
    """Test API endpoints"""
    BASE_URL = "http://localhost:8000/api"
    
    print("Testing API...")
    
    # Test 1: Health check endpoint
    try:
        response = requests.get(f"{BASE_URL.split('/api')[0]}/health")
        print(f"Health check: {response.status_code}")
        print(response.json())
    except Exception as e:
        print(f"Health check error: {str(e)}")
    
    # Test 2: Create content source
    try:
        source_data = {
            "name": "Test Source",
            "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
            "content_type": "website",
            "is_active": True
        }
        response = requests.post(f"{BASE_URL}/content/sources", json=source_data)
        print(f"Create content source: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        
        # If successful, get the source ID for further tests
        if response.status_code in (200, 201):
            source_id = response.json().get("id")
            
            # Test 3: Ingest content
            try:
                response = requests.post(f"{BASE_URL}/content/sources/{source_id}/ingest")
                print(f"Ingest content: {response.status_code}")
                print(json.dumps(response.json(), indent=2))
            except Exception as e:
                print(f"Ingest content error: {str(e)}")
            
            # Test 4: Get content items
            try:
                response = requests.get(f"{BASE_URL}/content/items", params={"source_id": source_id})
                print(f"Get content items: {response.status_code}")
                content_items = response.json()
                print(f"Number of items: {len(content_items)}")
                
                # If we have content items, test post generation
                if content_items:
                    content_item_id = content_items[0].get("id")
                    
                    # Test 5: Generate post
                    try:
                        post_data = {
                            "content_item_id": content_item_id,
                            "platform": "linkedin"
                        }
                        response = requests.post(f"{BASE_URL}/posts/generate", json=post_data)
                        print(f"Generate post: {response.status_code}")
                        print(json.dumps(response.json(), indent=2))
                    except Exception as e:
                        print(f"Generate post error: {str(e)}")
            except Exception as e:
                print(f"Get content items error: {str(e)}")
    except Exception as e:
        print(f"Create content source error: {str(e)}")

if __name__ == "__main__":
    test_api() 