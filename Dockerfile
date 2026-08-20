FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    HF_HUB_TIMEOUT=600 \
    TRANSFORMERS_CACHE=/code/.cache/huggingface

WORKDIR /code

# Create cache directory and grant access permissions
RUN mkdir -p /code/.cache/huggingface && chmod -R 777 /code/.cache

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . /code

# Set permissions for files
RUN chmod -R 777 /code

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
