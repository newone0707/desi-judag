FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    wget \
    unzip \
    && wget -q https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && unzip Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    && cp Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/mp4decrypt /usr/local/bin/ \
    && cp Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/mp4dump /usr/local/bin/ \
    && rm -rf Bento4-SDK-1-6-0-641.x86_64-unknown-linux* \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir --upgrade -r sainibots.txt \
    && pip3 install -U yt-dlp

CMD ["sh", "-c", "gunicorn app:app & python3 modules/main.py"]
