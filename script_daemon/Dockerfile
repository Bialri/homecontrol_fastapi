FROM python:3.11

WORKDIR /app

COPY requirements_build.txt /app/requirements_build.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements_build.txt

COPY . /app

CMD ["python","-u","main.py"]

