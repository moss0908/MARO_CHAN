FROM python:3.11-slim
WORKDIR /bot
COPY requirements.txt /bot/
# Install ffmpeg (required by yt-dlp for audio extraction) and other system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
	ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Use an up-to-date pip/setuptools/wheel before installing requirements
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
COPY . /bot
CMD python main.py