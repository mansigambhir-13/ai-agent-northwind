.PHONY: install test run docker-build docker-run clean

install:
    python -m venv venv
    . venv/bin/activate && pip install -r requirements.txt

test:
    . venv/bin/activate && python -m pytest tests/ -v

run:
    . venv/bin/activate && python main.py

web:
    . venv/bin/activate && python web_interface.py

docker-build:
    docker build -t northwind-ai-agent .

docker-run:
    docker run -p 8000:8000 --env-file .env northwind-ai-agent

clean:
    rm -rf venv/
    rm -f *.db
    rm -rf __pycache__/
    rm -rf .pytest_cache/

setup: install
    cp .env.example .env
    echo "✅ Development environment setup complete!"
    echo "📝 Please edit .env file with your OpenAI API key"
