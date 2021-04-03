FROM sasano8/basic_fastapi_selenium-standalone-chrome-debug:3.8 as builder
LABEL maintainer="sasano8"


USER root

ENV PYTHONPATH=/app

EXPOSE 80
EXPOSE 8080
EXPOSE 5672
EXPOSE 22

RUN sudo apt-get update && sudo apt install -y openssh-server && sudo apt install -y vim git
RUN sudo mkdir /run/sshd

RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
# COPY ./config_files/id_rsa.pub /root/.ssh/authorized_keys
RUN echo "root:secret" | chpasswd


WORKDIR /app/
RUN chown seluser:seluser /app

USER seluser
RUN poetry config virtualenvs.create false && poetry config virtualenvs.in-project false

# COPY ./pyproject.toml /app/pyproject.toml
# 存在する場合にコピーを行う場合、ワイルドカードが使用できる。ただし、存在するファイルを最低１つは指定しなければいけない
COPY pyproject.toml poetry.lock* /app/
COPY vendor /app/vendor
RUN sudo chgrp seluser /app/vendor

RUN sudo pip3 install --upgrade keyrings.alt

# sudoをつけないと、poetryがグローバルインストールされているため権限エラーが発生する
RUN sudo apt install -y graphviz libgraphviz-dev  # eralchemyのer出力にグラフライブラリが必要
# RUN sudo poetry update
RUN sudo poetry install



# development
RUN sudo apt-get update && sudo apt-get install -y sudo vim zsh git

# custom
RUN echo "alias ll='ls -l'" >> ~/.bashrc
RUN echo "alias ll='ls -l'" >> ~/.zshrc


# キャッシュを活用するため、ディレクトリ全体を更新は最後（ONBUILDは派生ビルド時に遅延実行される）
ONBUILD COPY . /

ONBUILD RUN sudo ln -s `pwd`/supervisor/fastapi.conf /etc/supervisor/conf.d/
ONBUILD RUN sudo ln -s `pwd`/supervisor/sshd.conf /etc/supervisor/conf.d/


FROM builder


ENV PYTHONUNBUFFERED=1

# debugpy
EXPOSE 5678

ARG CONTAINER_USER_ID
ARG CONTAINER_GROUP_ID

RUN sudo usermod -u ${CONTAINER_USER_ID:-1000} seluser
RUN sudo groupmod -g ${CONTAINER_GROUP_ID:-1000} seluser
RUN sudo usermod -aG root seluser


# dockerでマルチプロセスを管理する場合は、supervisorを利用する
CMD ["/opt/bin/entry_point.sh"]
# /opt/bin/start-selenium-standalone.sh --> セレニウムサーバ
# /opt/bin/start-xvfb.sh --> 仮想ディスプレイ（CUIモードでもセレニウムを動かせる）
# /opt/bin/start-fluxbox.sh --> X Windows
# /opt/bin/start-vnc.sh --> リモートデスクトップ

