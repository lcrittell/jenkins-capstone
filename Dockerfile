FROM python:3.12-slim

COPY . .

EXPOSE 8000

RUN echo "$APP_VERSION"

RUN sed -i "s/#APP_VERSION#/$APP_VERSION/g" index.html

CMD ["python", "app.py"]