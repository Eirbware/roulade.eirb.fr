# 
FROM python:3.11

# 
WORKDIR /EirbConnect

# 
COPY ./requirements.txt /EirbConnect/requirements.txt


# 
RUN pip install --no-cache-dir --upgrade -r /EirbConnect/requirements.txt

# 
COPY ./app /EirbConnect/app


ENV PORT 8080

EXPOSE 8080

# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips=*"]
