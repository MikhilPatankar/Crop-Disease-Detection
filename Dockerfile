FROM tensorflow/tensorflow:latest

WORKDIR /cdd

COPY . .
RUN pip3 install --no-cache-dir --ignore-installed -r requirements.txt

RUN addgroup --gid 10016 choreo && \
    adduser  --disabled-password  --no-create-home --uid 10016 --ingroup choreo choreouser

USER 10016

EXPOSE 5000
CMD [ "uvicorn", "backend.main:app", "--host=0.0.0.0", "--port=5000", "--reload", "--reload-dir=./backend" ]