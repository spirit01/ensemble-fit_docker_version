# Instal OS and basic commands
FROM fedora:28
RUN dnf -y install wget \
    &&  dnf -y install make \
    &&  dnf -y install python3-numpy \
    &&  dnf -y install wget python3-pip \
    && python3.6 -m pip install biopython fortranformat \
    && python3.6 -m pip install fortranformat \
    && dnf -y install gcc-c++ \
    && dnf -y install openmpi* \
    && yum -y clean all

# install IMP libraries
    COPY ./saxs-ensemble-fit/ /opt/ensemble-fit/
    COPY ./dependences/IMP/*.rpm /tmp/IMP/
    RUN dnf -y install /tmp/IMP/IMP-2.9*.rpm && \
        dnf -y install /tmp/IMP/IMP-devel*.rpm && \
        dnf -y install eigen3-devel && \
        dnf -y install make && yum -y clean all

#install MES
ENV PATH=$PATH:/usr/lib64/openmpi/bin
RUN wget http://bl1231.als.lbl.gov/pickup/mes.tar -O /tmp/mes.tar \
    && tar -xf /tmp/mes.tar -C /opt/ \
    && make clean -C /opt/weights/ \
    && make -C /opt/weights/

# prepare directory and install ensemble-fit
RUN make -C /opt/ensemble-fit/core/

#Run experiment in /opt/ensemble-test/src/
#docker run -it -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/data:/home/data ensemble bash
ENTRYPOINT ["/home/ensemble-test/run_script_ensemble"]
#TODO vyresit nastaveni CMD, aby se image poustel s timto
CMD ["-d" , "/home/data/foxs_curves/", "-n", "10", "-k","5","-r","3", "--experimentdata", "/home/data/experimental_data/exp.dat","--output","/home/ensemble-test/results/","--preserve","--verbose","3","--tolerance","1"]

 #reduce dockerfile size
 RUN yum clean all && rm -rf /var/cache/yum
