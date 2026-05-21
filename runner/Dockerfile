FROM klee/klee:v3.2

USER root
RUN mkdir -p /work && chown klee:klee /work

COPY --chown=klee:klee entrypoint.py /home/klee/entrypoint.py

USER klee
WORKDIR /work
ENTRYPOINT ["python3", "/home/klee/entrypoint.py"]