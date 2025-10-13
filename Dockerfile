FROM hub.dataloop.ai/dtlpy-runner-images/cpu:python3.10_opencv

RUN pip install --user \
    pymongo \
    pandas \
    dtlpy
