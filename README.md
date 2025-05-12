# Swym AI Social Media Content Agent

AI-powered platform for automated social media content generation and publishing across multiple platforms, including LinkedIn, Twitter, and Instagram.

## 🧠 Features

- **Content Ingestion**: Automatically scrape websites and process internal documents
- **Content Classification**: Intelligently categorize content using NLP
- **RAG-powered Generation**: Use Retrieval-Augmented Generation to create high-quality posts
- **Templated Images**: Generate branded social media images 
- **Multi-platform Publishing**: Schedule and publish to LinkedIn, Twitter, and Instagram
- **Analytics & Dashboard**: Review content performance metrics
- **Frontend UI**: Modern, responsive interface for entering URLs and viewing generated posts

## 🛠️ Tech Stack

- **Backend**: FastAPI + Pydantic
- **Frontend**: React + TailwindCSS
- **LLM + Agents**: OpenAI GPT-4 Turbo + LangGraph
- **Image Gen**: Pillow (PIL)
- **Ingestion**: BeautifulSoup + Playwright
- **Dashboard**: Streamlit (optional)
- **Database**: SQLAlchemy + PostgreSQL
- **Scheduler**: APScheduler / Celery + Redis
- **APIs**: LinkedIn, X, Instagram Graph API

## 📋 Setup & Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis (for Celery tasks)
- Node.js 16+ (for frontend)

### Environment Setup

1. Clone the repository:

```bash
git clone https://github.com/your-org/swym-content-agent.git
cd swym-content-agent
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.sample` and configure your environment variables:

```
# Application settings
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your_secret_key_here

# Database settings
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/swym_social

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Social Media API Keys
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here

# ...additional settings
```

5. Initialize the database:

```bash
alembic upgrade head
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd app/frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the frontend development server:

```bash
npm start
```

The frontend will be available at http://localhost:3000.

## 🚀 Running the Application

Start the FastAPI server:

```bash
python main.py
```

The API will be available at http://localhost:8000, with interactive documentation at http://localhost:8000/docs.

## 📊 Usage

### Using the Frontend UI

1. Open the frontend application at http://localhost:3000
2. Enter a URL in the input field
3. Click "Generate Content"
4. Wait for the content to be extracted and posts to be generated
5. View the generated social media posts for LinkedIn, Twitter, and Instagram

### Content Ingestion

To add a new content source:

```python
from app.ingestion.scraper import WebScraper
from app.models.content import ContentSource, ContentType
from app.models.database import SessionLocal

db = SessionLocal()
source = ContentSource(
    name="Company Blog",
    url="https://example.com/blog",
    content_type=ContentType.BLOG,
    is_active=True
)
db.add(source)
db.commit()

scraper = WebScraper(db)
content_items = scraper.scrape_website(source)
db.add_all(content_items)
db.commit()
```

### Post Generation

To generate a new social media post:

```python
from app.agents.post_generator import PostGenerator
from app.models.content import Platform

generator = PostGenerator()
post = generator.generate_post(content_item, Platform.LINKEDIN)
db.add(post)
db.commit()
```

### Scheduling Posts

To schedule a post for publication:

```python
from app.scheduler.post_scheduler import PostScheduler
from datetime import datetime, timedelta

scheduler = PostScheduler(db)
scheduler.start()

# Schedule post for tomorrow at 10 AM
publish_time = datetime.utcnow() + timedelta(days=1)
publish_time = publish_time.replace(hour=10, minute=0, second=0)
scheduler.schedule_post(post, publish_time)
```

## 📑 Project Structure

- `app/`: Main application package
  - `agents/`: AI agent modules 
  - `api/`: API endpoints and routes
  - `frontend/`: React frontend application
  - `ingestion/`: Content ingest and processing
  - `models/`: Database models
  - `retrieval/`: RAG retrieval service
  - `scheduler/`: Scheduling and publishing
  - `services/`: External API integrations
  - `templates/`: Image template generation
- `data/`: Data storage
- `tests/`: Unit and integration tests
- `scripts/`: Utility scripts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details. 