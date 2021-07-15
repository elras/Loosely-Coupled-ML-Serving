FROM pytorch/pytorch:1.8.0-cuda11.1-cudnn8-runtime
RUN python -m pip install -r requirements.txt
COPY . /worker
WORKDIR /worker
CMD exec python run.py