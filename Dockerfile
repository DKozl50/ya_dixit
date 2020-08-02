FROM ubuntu:18.04 as builder

WORKDIR /usr/src/app

RUN apt update && apt install -y wget &&\
    wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt update && \
    apt install -y nodejs npm apt-transport-https && \
    apt update && \
    apt install -y dotnet-sdk-3.1 && \
    npm i npm@latest -g

COPY front/ front/
WORKDIR front
RUN dotnet restore && \
    npm install && \
    npm run build

FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt --no-cache-dir
RUN rm -rf /tmp

COPY back/ back/
COPY --from=builder /usr/src/app/front/deploy back/tic_tac_toe/static

CMD python back/tic_tac_toe/Server.py