# How to build image https://docs.docker.com/engine/reference/commandline/build/ 
# > cd into this folder
# > docker build -t <image_name> .
# (no tag no work)
# How to run it https://docs.docker.com/engine/reference/commandline/run/
# > docker run -p 8888:8888 <image_name>
# Or actually more convenient from the docker UI, but remember to map 8888 to 8888
# the link to execute the notebook is in the console as this image boots up. It will look like this with a token:
# http://127.0.0.1:8888/lab?token=4f682b43edfeb4f0139ade0eb1b7190e0bbb030c6056601b

# https://github.com/jupyter/docker-stacks/tree/main/minimal-notebook
FROM jupyter/minimal-notebook

# Temporary elevation
USER root

# Install MiniZinc https://www.minizinc.org/
RUN apt-get update
RUN apt-get install --yes minizinc

# Install Python 3 packages
RUN mamba install --quiet --yes sqlglot

# Install Optimathsat https://optimathsat.disi.unitn.it/
COPY optimathsat /usr/bin

# Install ACT_Conveyance_Duty.ipynb
COPY work/query_idr_magic.py /home/${NB_USER}/work
COPY work/idr_query.py /home/${NB_USER}/work
COPY work/act_conveyance_duty.mzn /home/${NB_USER}/work
COPY ACT_Conveyance_Duty.ipynb /home/${NB_USER}

# Return to User level
USER ${NB_UID}


