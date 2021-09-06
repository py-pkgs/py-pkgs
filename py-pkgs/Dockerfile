FROM rocker/verse:4.1.1

# System dependencies
RUN apt-get update && apt-get install -y \
    python3-pip

# Install Python dependencies
RUN pip3 install \
    jupytext

# Install LaTeX packages
RUN tlmgr install amsmath \
    latex-amsmath-dev \
    fontspec \
    tipa \
    unicode-math \
    xunicode \
    kvoptions \
    ltxcmds \
    kvsetkeys \
    etoolbox \
    xcolor \
    auxhook \
    bigintcalc \
    bitset \
    etexcmds \
    gettitlestring \
    hycolor \
    hyperref \
    intcalc \
    kvdefinekeys \
    letltxmacro \
    pdfescape \
    refcount \
    rerunfilecheck \
    stringenc \
    uniquecounter \
    zapfding \
    pdftexcmds \
    infwarerr \
    fancyvrb \
    framed \
    booktabs \
    mdwtools \
    grffile \
    caption \
    sourcecodepro \
    amscls \
    natbib

# increase the ImageMagick resource limits
RUN sed -i 's/256MiB/4GiB/' /etc/ImageMagick-6/policy.xml
RUN sed -i 's/512MiB/4GiB/' /etc/ImageMagick-6/policy.xml
RUN sed -i 's/1GiB/4GiB/' /etc/ImageMagick-6/policy.xml