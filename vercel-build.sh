#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright with minimal dependencies
python -m playwright install --with-deps chromium

# Create a Vercel output directory
mkdir -p .vercel/output/static
mkdir -p .vercel/output/functions

# Create a simplified output configuration for Vercel
cat > .vercel/output/config.json << EOF
{
  "version": 3,
  "routes": [
    { "handle": "filesystem" },
    { "src": "/(.*)", "dest": "/api/index.py" }
  ]
}
EOF

# Copy the main application code to the function directory
cp -r main.py app .vercel/output/functions/api/

# Create simplified entrypoint for Vercel
cat > .vercel/output/functions/api/index.py << EOF
from app.api.app import app

# For Vercel serverless functions, we expose the app object directly
# The app is already imported from app.api.app
EOF 