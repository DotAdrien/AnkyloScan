FROM python:3.9-slim
RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y wine wine32 gcc-mingw-w64
RUN pip install pyinstaller fastapi uvicorn
WORKDIR /app
COPY compiler_api.py .
CMD ["uvicorn", "compiler_api:app", "--host", "0.0.0.0", "--port", "8002"]