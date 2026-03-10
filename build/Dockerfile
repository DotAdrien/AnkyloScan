FROM python:3.11-slim

RUN apt-get update && apt-get install -y g++-mingw-w64-x86-64

RUN pip install --no-cache-dir fastapi uvicorn

WORKDIR /app
COPY compiler_api.py .
COPY agent_template.cpp . 

CMD ["python", "-m", "uvicorn", "compiler_api:app", "--host", "0.0.0.0", "--port", "8002"]