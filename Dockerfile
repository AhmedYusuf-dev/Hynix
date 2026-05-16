# Project Identity: Hynix 1 Mini Kernel
# Platform: Hugging Face Spaces (Docker)

FROM python:3.12

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the entire Hynix ecosystem
COPY --chown=user . .

# Hynix Cloud Mode: Port must be 7860 for Hugging Face
# We use the backend.main:app module path
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
