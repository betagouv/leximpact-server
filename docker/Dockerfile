FROM python:3.7
WORKDIR /opt
RUN apt-get update && apt-get -y install libyaml-dev libhdf5-serial-dev postgresql-client

WORKDIR /opt/leximpact-server
# Tips : relative path is from root project folder as we use context in docker-compose
#COPY ./docker/.env.docker .env
COPY Makefile .
COPY setup.py .
# TODO : For unknown reseon we have to intall numpy to make "Building wheel for tables (setup.py)" work
# Despite it exist in dependancies.
RUN pip install numpy
RUN make install

#COPY package.json .
# Install dependencies
# RUN npm update
# RUN npm install
#make test
#CMD ["npm", "run", "dev"]
#ENTRYPOINT ["watch", "-n", "60", "echo 'Client is in debug...'"]
#COPY entrypoint.sh .
#RUN chmod a+x entrypoint.sh
EXPOSE 5000
ENTRYPOINT ["/opt/leximpact-server/docker/entrypoint.sh"]