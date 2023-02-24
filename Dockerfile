FROM ubuntu:20.04

# Timezone Set
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# System requirements
RUN apt-get -y update && apt-get install -y \
    git \
    gnupg \
    python3 \
    python3-pip \
    sudo \
    udev \
    vim \
    wget

# C-driver for picoscope
# 1. Import public key
RUN wget -O - https://labs.picotech.com/debian/dists/picoscope/Release.gpg.key \
    | sudo apt-key add -
# 2. Configure system repository  
RUN echo "deb https://labs.picotech.com/rc/picoscope7/debian/ picoscope main" \
    > /etc/apt/sources.list.d/picoscope7.list
# 3. Update permissions
RUN mv /bin/udevadm /bin/udevadm.bin \
    && echo '#!/bin/bash' \
    > /bin/udevadm && chmod a+x /bin/udevadm
# 4. Actual installation
# Note: only installing libps4000 driver as opposed to 'picoscope' which installs all of them
RUN apt-get -y update && apt-get install -y \
    libps4000 \
    libps2000a

# Pico repo
RUN git clone --branch pulsing https://github.com/steingartlab/acoustics_hardware.git
WORKDIR /acoustics_hardware
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]