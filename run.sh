#!/bin/bash
set -e

echo "🚀 Starting Northwind AI Agent System"

if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please create one using .env.example"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

source venv/bin/activate

echo "📋 Installing dependencies..."
pip install -r requirements.txt

echo "🤖 Starting AI Agent..."
python main.py
