FROM qgis/qgis:release-3_12 as tester

# Install python packages
RUN pip3 install --no-cache-dir \
    pydevd \
    pytest
