# Deploying to Vercel

This guide explains how to deploy the Swym AI Social Media Content Agent to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. The [Vercel CLI](https://vercel.com/cli) installed (optional but recommended)
3. A PostgreSQL database (e.g., Supabase, Railway, Neon, etc.)
4. A Redis instance (if using Celery for background tasks)

## Steps to Deploy

### 1. Prepare Your Repository

The repository is already configured with the necessary Vercel configuration files:
- `vercel.json` - Configures the Vercel deployment
- `.vercelignore` - Specifies files to exclude from deployment

### 2. Set Up Environment Variables

In your Vercel project settings, add the following environment variables:

```
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your_production_secret_key
DATABASE_URL=your_postgres_connection_string
OPENAI_API_KEY=your_openai_api_key
REDIS_URL=your_redis_url
```

Add any other environment variables required for your specific setup (LinkedIn, Twitter, Instagram, etc.).

### 3. Deploy to Vercel

#### Using GitHub Integration

1. Push your code to GitHub
2. Log in to Vercel and create a new project
3. Select your repository
4. Configure the settings:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: None needed
   - Output Directory: None needed
5. Add the environment variables
6. Click "Deploy"

#### Using Vercel CLI

1. Login to Vercel:
   ```
   vercel login
   ```

2. Deploy from the project directory:
   ```
   vercel
   ```

3. Follow the prompts to set up your project
4. Set environment variables:
   ```
   vercel env add DATABASE_URL
   vercel env add OPENAI_API_KEY
   # Add other environment variables as needed
   ```

5. Deploy to production:
   ```
   vercel --prod
   ```

### 4. Database Migrations

After deployment, you'll need to run database migrations. Using Vercel's "Functions" tab, run:

```
vercel run -- alembic upgrade head
```

Or connect to your deployed database directly and run migrations locally.

## Important Notes

1. **PostgreSQL Database**: Vercel doesn't provide PostgreSQL databases. Use a service like Supabase, Railway, or Neon.

2. **Serverless Limitations**: Vercel functions have a maximum execution time of 10 seconds for the Hobby plan (up to 60 seconds on Pro plans). Long-running processes should be offloaded to background tasks.

3. **Redis and Background Tasks**: If using Celery with Redis, you'll need a separate Redis service (e.g., Upstash, Redis Labs).

4. **SQLite**: The local SQLite database (`swym_social.db`) won't work on Vercel. Make sure to use PostgreSQL.

5. **File Storage**: Vercel functions don't have persistent file storage. Use cloud storage solutions like S3 for any file storage needs.

## Troubleshooting

If you encounter issues with your deployment:

1. Check the Vercel deployment logs
2. Verify all environment variables are set correctly
3. Ensure your database is accessible from Vercel's IP ranges
4. Check that your application is compatible with serverless functions 