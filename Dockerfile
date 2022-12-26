# How to build image https://docs.docker.com/engine/reference/commandline/build/  
# > cd into this folder
# > docker build -t <image_name> .
# (no tag no srcx)
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

# Install pip
RUN apt-get install --yes python3-pip

# Install Python 3 packages
COPY srcx/requirements.txt /home/${NB_USER}/srcx
RUN pip install -r /home/${NB_USER}/srcx/requirements.txt

# Install Optimathsat https://optimathsat.disi.unitn.it/
COPY bin/optimathsat /usr/bin
RUN chmod 755 /usr/bin/optimathsat
# Install ACT_Conveyance_Duty.ipynb
COPY srcx/query_idr_magic.py /home/${NB_USER}/srcx
COPY srcx/idr_query.py /home/${NB_USER}/srcx
COPY srcx/act_conveyance_duty.mzn /home/${NB_USER}/srcx
COPY ACT_Conveyance_Duty.ipynb /home/${NB_USER}
COPY srcx/test_idr_query.py /home/${NB_USER}/srcx
# Return to User level
USER ${NB_UID}


