curl -X POST http://localhost:8000/api/content/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Company Blog",
    "url": "https://www.getswym.com/blogs/what-your-shoppers-do-when-you-dont-have-a-wishlist-feature",
    "content_type": "website",
    "is_active": true
  }'