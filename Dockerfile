FROM camptocamp/qgis-server:latest

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir pytest
# used for calling the qgis api for the tests
RUN cp -r /usr/local/share/qgis/python/qgis /usr/local/lib/python3.6/dist-packages/
