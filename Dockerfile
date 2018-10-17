# Instal OS and basic commands
FROM fedora:28
RUN dnf -y install wget

# install IMP libraries
COPY ./dependences/IMP/*.rpm /tmp/IMP/
COPY ./src/ /home/ensemble-test/src/
COPY ./examples_I/ /home/ensemble-test/examples_I/
COPY ./examples_II/ /home/ensemble-test/examples_II/
COPY ./experimental_data/ /home/ensemble-test/experimental_data/

RUN dnf -y install /tmp/IMP/IMP-*.rpm
RUN dnf -y install eigen3-devel
RUN dnf -y install vim
RUN dnf -y install make

# prepare directory and install ensemble-fit
COPY ./saxs-ensamble-fit/ /home/ensemble-fit/
RUN dnf -y install openmpi*
ENV PATH=$PATH:/usr/lib64/openmpi/bin
RUN make -C /home/ensemble-fit/core/

#install MES
RUN wget http://bl1231.als.lbl.gov/pickup/mes.tar -O /tmp/mes.tar
RUN tar -xf /tmp/mes.tar -C /home/
RUN make clean -C /home/weights/
RUN make -C /home/weights/

#install GAJOE
# You must download files and put them in dependences dictionary.
# Visit: https://www.embl-hamburg.de/biosaxs/atsas-online/download.php
# and download 2.8.4.openSUSE-42.
# ATSAS-2.8.4-1.SUSE-42.x86_64.rpm extract to /dependences
# and run
COPY ./dependences/ATSAS-2.8.4-1.SUSE-42.x86_64.rpm /tmp/eom/
RUN dnf -y install /tmp/eom/ATSAS-2.8.4-1.SUSE-42.x86_64.rpm
