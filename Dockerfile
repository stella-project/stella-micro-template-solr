FROM solr:latest

USER root
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip


USER solr

COPY . .

USER root
RUN pip3 install -r requirements.txt
RUN sed -i -e '2inohup python3 app.py &\' /opt/docker-solr/scripts/docker-entrypoint.sh

RUN mkdir -p /opt/"solr-8.8.1"/server/solr/configsets/livivo/conf
COPY index_settings/livivo/ /opt/solr-8.8.1/server/solr/configsets/livivo/

#RUN mkdir -p /opt/"solr-8.8.1"/server/solr/configsets/documents/conf
#COPY index_settings/gesis/documents/conf/ /opt/solr-8.8.1/server/solr/configsets/documents/conf/

RUN mkdir -p /opt/"solr-8.8.1"/server/solr/configsets/datasets/conf
COPY index_settings/gesis/datasets/conf/ /opt/solr-8.8.1/server/solr/configsets/datasets/conf/

USER solr
EXPOSE 5000/tcp
EXPOSE 8983/tcp
