FROM python:3

WORKDIR app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN rm -rf /var/log/compute.log

CMD [ "python", "./main.py"]
