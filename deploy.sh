#!/bin/bash

# Recipe API Vercel Deployment Script

echo "🚀 Preparing Recipe API for Vercel deployment..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "npm i -g vercel"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please create one based on .env.example"
    echo "Make sure to set your LLM7_TOKEN"
    exit 1
fi

echo "✅ Environment setup looks good!"

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod

echo "🎉 Deployment complete!"
echo ""
echo "📋 Post-deployment checklist:"
echo "1. Set environment variables in Vercel dashboard:"
echo "   - LLM7_TOKEN (from https://token.llm7.io/)"
echo "   - API_HOST=0.0.0.0"
echo "   - API_PORT=8000"
echo "   - DEBUG=False"
echo ""
echo "2. Test your API endpoints:"
echo "   - GET /health"
echo "   - POST /api/recipes/from-ingredients"
echo "   - POST /api/recipes/from-image"
echo ""
echo "3. Check the /docs endpoint for interactive API documentation"
