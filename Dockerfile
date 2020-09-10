FROM python:latest

# Install dependencies.
ADD main.py /main.py
RUN pip install -r pygithub

CMD ["python", "/main.py"]