FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not create virtual env in container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy source code
COPY company_valuation/ ./company_valuation/
COPY tests/ ./tests/
COPY examples/ ./examples/

# Install the package
RUN poetry install --no-interaction --no-ansi

# Default command runs tests
CMD ["pytest", "-v"]
