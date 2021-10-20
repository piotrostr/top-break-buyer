FROM python:latest
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y build-essential
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xzf ta-lib-0.4.0-src.tar.gz 
RUN cd ta-lib && \  
  ./configure --build=x86_64 && \
  make && \
  make install && \
  cd -
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]

