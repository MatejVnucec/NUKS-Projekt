FROM python:3.10.6-buster

ENV APPROOT="/home/app/web" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VERSION="0.1" 

LABEL base.name="Smart API" \
      base.version="${VERSION}"

RUN groupadd -r -g 2200 app && \
    useradd -rM -g app -u 2200 app

WORKDIR $APPROOT

EXPOSE 8000

RUN apt-get update && apt-get install -y \
    --no-install-recommends netcat \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY ./requirements.txt $APPROOT/requirements.txt
RUN pip install -r requirements.txt
COPY . $APPROOT

RUN chown -R app:app $APPROOT

USER app

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]