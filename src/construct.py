from config import TugboatConfig
import json
import os
import prompt_toolkit as pt
import re
import subprocess
import time
import urllib.request
from utils import hash_text
import webbrowser
import yaml

class DockerfileGenerator:
    """Create a Dockerfile from a local directory.
    
    DockerfileGenerator will ingest a configuration file from a local directory
    and, in turn, will spit out a corresponding Docker file containing all files
    in the directory as well as any required software.
    
    Parameters
    ----------
    config : TugboatConfig
        An object of class `TugboatConfig`. This should include all relevant
        configuration settings for building our Docker image.
    
    Attributes
    ----------
    config : dict
        Configuration settings structured as a dictionary.
    requirements : list of str
        A list of all software requirements.
    
    Methods
    -------
    """
    def __init__(self, config: TugboatConfig):
        self.config = config.config
        self.requirements = config.requirements
        self._dockerfile = ""
        self._dockerignore = ""
        self._using_existing_dockerfile = False
    
    def _dockerignore_create(self, *args):
        dockerignore = (
            "Dockerfile\n.dockerignore\n.dockerenv\n.Rhistory\n.Rprofile\n"
            + ".Rproj.user\n.git\nrenv\n"
        )
        return dockerignore
    
    def _dockerfile_julia(self):
        julia_version = self._software_version("Julia", "latest")
        julia_install = (
            f"ENV JULIA_VERSION={julia_version}"
            + "\nRUN rocker_scripts/install_julia.sh\n\n"
        )
        if not "Julia" in self.requirements:
            julia_install = ""
        return julia_install
    
    def _dockerfile_jupyter(self):
        jupyter_install = (
            "RUN apt-get update && \\"
            + "\n    apt-get install -y --no-install-recommends libpng-dev \\"
            + "\n    swig \\"
            + "\n    libzmq3-dev && \\"
            + "\n    pip install --upgrade pip && \\"
            + "\n    pip install --no-cache-dir notebook jupyterlab jupyterhub && \\"
            + "\n    R -e 'renv::install(\"IRkernel/IRkernel@*release\")' && \\"
            + "\n    R -e 'IRkernel::installspec(user = FALSE)' && \\"
            + "\n    echo -e \"#!/bin/bash\\n\\"
            + "\n# Start Jupyter Lab and redirect its output to the console\\n\\"
            + "\nnohup jupyter lab --ip=0.0.0.0 --port=8888 --allow-root --notebook-dir=/tugboat_dir --no-browser > /jupyter.log 2>&1 &\\n\\"
            + "\n# Use 'tail' to keep the script running\\n\\"
            + "\ntail -f /jupyter.log\" >> /init_jupyter && \\"
            + "\n    chmod +x /init_jupyter"
            + "\n\nEXPOSE 8888\n\n"
        )
        if not "Jupyter" in self.requirements:
            jupyter_install = ""
        return jupyter_install
    
    def _dockerfile_pandoc(self):
        pandoc_version = self._software_version("Pandoc", "default")
        pandoc_install = (
            f"ENV PANDOC_VERSION=\"{pandoc_version}\""
            + "\nRUN rocker_scripts/install_pandoc.sh\n\n"
        )
        if not "Pandoc" in self.requirements:
            pandoc_install = ""
        return pandoc_install
    
    def _dockerfile_prelude(self):
        r_version = self._software_version("R", "latest")
        prelude = (
            f"FROM rocker/r-ver:{r_version}"
            + "\n\n"
            + "SHELL [\"/bin/bash\", \"-c\"]"
            + "\n\n"
            + "COPY ./ ./tugboat_dir"
            + "\n\n"
            + "RUN source /etc/os-release && \\"
            + "\n    R -e \"install.packages('renv')\"\n\n"
        )
        return prelude
    
    def _dockerfile_python(self):
        python_version = self._software_version("Python")
        if not python_version == None:
            python_install = f"ENV PYTHON_VERSION={python_version}\n"
            mamba_install = "\n    mamba install -y python=${PYTHON_VERSION} && \\"
        else:
            python_install = ""
            mamba_install = "\n    mamba install -y python && \\"
        python_install = (
            python_install
            + "ENV CONDA_DIR=/srv/conda"
            + "\nENV VENV=/opt/.venv"
            + "\nENV PATH=${CONDA_DIR}/bin:${PATH}"
            + "\nRUN apt-get update && \\"
            + "\n    apt-get install -y curl && \\"
            + "\n    echo \"Installing Mambaforge...\" && \\"
            + "\n    curl -sSL \"https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh\" > installer.sh && \\"
            + "\n    /bin/bash installer.sh -u -b -p ${CONDA_DIR} && \\"
            + "\n    rm installer.sh && \\"
            + "\n    mamba clean -afy && \\"
            + "\n    find ${CONDA_DIR} -follow -type f -name '*.a' -delete && \\"
            + "\n    find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete && \\"
            + mamba_install
            + "\n    python3 -m venv ${VENV}"
            + "\nENV PATH=${VENV}/bin:${PATH}"
            + "\nRUN echo \"PATH=${PATH}\" >> /usr/local/lib/R/etc/Renviron.site && \\"
            + "\n    echo \"export PATH=${PATH}\" >> /etc/profile"
            + "\nENV RETICULATE_PYTHON=\"${VENV}/bin/python\" && \\"
            + "\nR -e \"renv::install('reticulate', prompt = FALSE, type = 'binary')\"\n\n"
        )
        if not "Python" in self.requirements:
            python_install = ""
        return python_install
    
    def _dockerfile_postlude(self):
        postlude = (
            "RUN chmod -R a+rwX /opt && \\"
            + "\n    chmod -R a+rwX /srv && \\"
            + "\n    chmod -R a+rwX /tugboat_dir"
            + "\n\nCMD [\"/bin/bash\"]"
        )
        return postlude
    
    def _dockerfile_pydeps(self):
        py_deps = (
            "RUN pip install pipreqs pipreqsnb && \\"
            + "\n    pipreqs --savepath requirements-scripts.txt ./ || true && \\"
            + "\n    pipreqsnb --savepath requirements-nbs.txt ./ || true && \\"
            + "\n    [ -f requirements.txt ] && pip install -r requirements.txt || true && \\"
            + "\n    [ -f requirements-scripts.txt ] && pip install -r requirements-scripts.txt || true && \\"
            + "\n    [ -f requirements-nbs.txt ] && pip install -r requirements-nbs.txt || true && \\"
            + "\n    [ -f requirements-scripts.txt ] && rm -f requirements-scripts.txt || true && \\"
            + "\n    [ -f requirements-nbs.txt ] && rm -f requirements-nbs.txt || true\n\n"
        )
        if not "Python" in self.requirements:
            py_deps = ""
        return py_deps
    
    def _dockerfile_quarto(self):
        quarto_version = self._software_version("Quarto", "default")
        quarto_install = (
            f"ENV QUARTO_VERSION=\"{quarto_version}\""
            + "\nRUN rocker_scripts/install_quarto.sh\n\n"
        )
        if not "Quarto" in self.requirements:
            quarto_install = ""
        return quarto_install
    
    def _dockerfile_remove(self, silent=True):
        dockerfile_path = "Dockerfile"
        dockerignore_path = ".dockerignore"
        if os.path.isfile(dockerfile_path):
            os.remove(dockerfile_path)
            return True
        elif silent:
            return True
        else:
            raise Exception(f"No Dockerfile exists at the following location: {os.path.realpath(dockerfile_path)}")
        if os.path.isfile(dockerignore_path):
            os.remove(dockerignore_path)
            return True
        elif silent:
            return True
        else:
            raise Exception(f"No .dockerignore file exists at the following location: {os.path.realpath(dockerignore_path)}")
        return None
    
    def _dockerfile_rstudio(self):
        with urllib.request.urlopen("https://www.rstudio.com/wp-content/downloads.json") as url:
            j = json.load(url)
            v = j.get("rstudio").get("open_source").get("stable").get("version")
        rs_version = self._software_version("RStudio", v)
        rs_install = (
            f"ENV RSTUDIO_VERSION=\"{rs_version}\""
            "\nRUN source /etc/os-release && \\"
            + "\n    apt-get update && \\"
            + "\n    apt-get install -y --no-install-recommends ca-certificates \\"
            + "\n    lsb-release \\"
            + "\n    file \\"
            + "\n    git \\"
            + "\n    libapparmor1 \\"
            + "\n    libclang-dev \\"
            + "\n    libcurl4-openssl-dev \\"
            + "\n    libedit2 \\"
            + "\n    libobjc4 \\"
            + "\n    libssl-dev \\"
            + "\n    libpq5 \\"
            + "\n    psmisc \\"
            + "\n    procps \\"
            + "\n    python-setuptools \\"
            + "\n    pwgen \\"
            + "\n    sudo \\"
            + "\n    wget && \\"
            + "\n    ARCH=$(dpkg --print-architecture) && \\"
            + "\n    /rocker_scripts/install_s6init.sh && \\"
            + "\n    DOWNLOAD_FILE=rstudio-server.deb && \\"
            + "\n    wget \"https://s3.amazonaws.com/rstudio-ide-build/server/${UBUNTU_CODENAME}/${ARCH}/rstudio-server-${RSTUDIO_VERSION/'+'/'-'}-${ARCH}.deb\" -O \"$DOWNLOAD_FILE\" && \\"
            + "\n    gdebi -n \"$DOWNLOAD_FILE\" && \\"
            + "\n    rm \"$DOWNLOAD_FILE\" && \\"
            + "\n    ln -fs /usr/lib/rstudio-server/bin/rstudio-server /usr/local/bin && \\"
            + "\n    ln -fs /usr/lib/rstudio-server/bin/rserver /usr/local/bin && \\"
            + "\n    rm -f /var/lib/rstudio-server/secure-cookie-key && \\"
            + "\n    mkdir -p /etc/R && \\"
            + "\n    R_BIN=$(which R) && \\"
            + "\n    echo \"rsession-which-r=${R_BIN}\" >/etc/rstudio/rserver.conf && \\"
            + "\n    echo \"lock-type=advisory\" >/etc/rstudio/file-locks && \\"
            + "\n    cp /etc/rstudio/rserver.conf /etc/rstudio/disable_auth_rserver.conf && \\"
            + "\n    echo \"auth-none=1\" >>/etc/rstudio/disable_auth_rserver.conf && \\"
            + "\n    mkdir -p /etc/services.d/rstudio && \\"
            + "\n    echo -e '#!/usr/bin/with-contenv bash\\n\\"
            + "\n## load /etc/environment vars first:\\n\\"
            + "\nfor line in $( cat /etc/environment ) ; do export $line > /dev/null; done\\n\\"
            + "\nexec /usr/lib/rstudio-server/bin/rserver --server-daemonize 0' >/etc/services.d/rstudio/run && \\"
            + "\n    echo -e '#!/bin/bash\\n\\"
            + "\n/usr/lib/rstudio-server/bin/rstudio-server stop' >/etc/services.d/rstudio/finish && \\"
            + "\n    if [ -n \"$CUDA_HOME\" ]; then \\"
            + "\n        sed -i '/^rsession-ld-library-path/d' /etc/rstudio/rserver.conf && \\"
            + "\n        echo \"rsession-ld-library-path=$LD_LIBRARY_PATH\" >>/etc/rstudio/rserver.conf ; \\"
            + "\n    fi && \\"
            + "\n    echo -e '[*]\\n\\"
            + "\nlog-level=warn\\n\\"
            + "\nlogger-type=syslog' >/etc/rstudio/logging.conf && \\"
            + "\n    /rocker_scripts/default_user.sh \"rstudio\" && \\"
            + "\n    cp /rocker_scripts/init_set_env.sh /etc/cont-init.d/01_set_env && \\"
            + "\n    cp /rocker_scripts/init_userconf.sh /etc/cont-init.d/02_userconf && \\"
            + "\n    cp /rocker_scripts/pam-helper.sh /usr/lib/rstudio-server/bin/pam-helper && \\"
            + "\n    rm -rf /var/lib/apt/lists/* && \\"
            + "\n    echo -e \"# /etc/rstudio/rsession.conf\\nsession-default-working-dir=/tugboat_dir\" >> /etc/rstudio/rsession.conf && \\"
            + "\n    echo -e \"\\nInstall RStudio Server, done!\""
            + "\n\nEXPOSE 8787\n\n"
        )
        if not "RStudio" in self.requirements:
            rs_install = ""
        return rs_install
    
    def _dockerfile_rdeps(self):
        r_deps = (
            "RUN source /etc/os-release && \\"
            + "\n    R -e \"if(file.exists('./renv.lock')) { lockfile <- renv::lockfile_read('./renv.lock'); exclude_pkgs <- c('base', 'boot', 'class', 'cluster', 'codetools', 'compiler', 'datasets', 'docopt', 'foreign', 'graphics', 'grDevices', 'grid', 'KernSmooth', 'lattice', 'littler', 'MASS', 'Matrix', 'methods', 'mgcv', 'nlme', 'nnet', 'parallel', 'rpart', 'spatial', 'splines', 'stats', 'stats4', 'survival', 'tcltk', 'tools', 'utils', 'renv'); updated_lockfile_pkgs <- lockfile[['Packages']][!names(lockfile[['Packages']]) %in% exclude_pkgs]; lockfile[['Packages']] <- updated_lockfile_pkgs; print(sort(names(lockfile[['Packages']]))); renv::lockfile_write(lockfile, './renv.lock') }\" && \\"
            + "\n    R -e \"if(file.exists('./renv.lock')) { renv::restore(lockfile = './renv.lock', prompt = FALSE) }\" && \\"
            + "\n    R -e \"renv::install(c('yaml'), prompt = FALSE, type = 'binary')\" && \\"
            + "\n    R -e \"install <- function(package) { if (isFALSE(require(package, quietly = TRUE, character.only = TRUE))) { tryCatch({ renv::install(package, prompt = FALSE, type = 'binary') }, error = function(err) cat('Failed to install', package, '\\n')) } }; r_deps <- renv::dependencies(); lapply(r_deps[['Package']], install)\"\n\n"
        )
        if not "R" in self.requirements:
            r_deps = ""
        return r_deps
    
    def _dockerfile_system_dependencies(self):
        sys_deps = (
            "RUN source /etc/os-release && \\"
            + "\n    apt-get update && \\"
            + "\n    apt-get install -y --no-install-recommends libxkbcommon-x11-0 \\"
            + "\n    ca-certificates \\"
            + "\n    lsb-release \\"
            + "\n    file \\"
            + "\n    git \\"
            + "\n    libapparmor1 \\"
            + "\n    libclang-dev \\"
            + "\n    libcurl4-openssl-dev \\"
            + "\n    libedit2 \\"
            + "\n    libobjc4 \\"
            + "\n    libssl-dev \\"
            + "\n    libpq5 \\"
            + "\n    psmisc \\"
            + "\n    procps \\"
            + "\n    python-setuptools \\"
            + "\n    pwgen \\"
            + "\n    sudo \\"
            + "\n    wget \\"
            + "\n    gdebi-core \\"
            + "\n    libcairo2-dev \\"
            + "\n    libxml2-dev \\"
            + "\n    libgit2-dev \\"
            + "\n    default-libmysqlclient-dev \\"
            + "\n    libpq-dev \\"
            + "\n    libsasl2-dev \\"
            + "\n    libsqlite3-dev \\"
            + "\n    libssh2-1-dev \\"
            + "\n    libxtst6 \\"
            + "\n    libharfbuzz-dev \\"
            + "\n    libfribidi-dev \\"
            + "\n    libfreetype6-dev \\"
            + "\n    libtiff5-dev \\"
            + "\n    libjpeg-dev \\"
            + "\n    unixodbc-dev \\"
            + "\n    gdal-bin \\"
            + "\n    lbzip2 \\"
            + "\n    libfftw3-dev \\"
            + "\n    libgdal-dev \\"
            + "\n    libgeos-dev \\"
            + "\n    libgsl0-dev \\"
            + "\n    libgl1-mesa-dev \\"
            + "\n    libglu1-mesa-dev \\"
            + "\n    libhdf4-alt-dev \\"
            + "\n    libhdf5-dev \\"
            + "\n    libjq-dev \\"
            + "\n    libproj-dev \\"
            + "\n    libprotobuf-dev \\"
            + "\n    libnetcdf-dev \\"
            + "\n    libudunits2-dev \\"
            + "\n    netcdf-bin \\"
            + "\n    postgis \\"
            + "\n    protobuf-compiler \\"
            + "\n    sqlite3 \\"
            + "\n    tk-dev \\"
            + "\n    cmake \\"
            + "\n    default-jdk \\"
            + "\n    fonts-roboto \\"
            + "\n    ghostscript \\"
            + "\n    hugo \\"
            + "\n    less \\"
            + "\n    libbz2-dev \\"
            + "\n    libglpk-dev \\"
            + "\n    libgmp3-dev \\"
            + "\n    libhunspell-dev \\"
            + "\n    libicu-dev \\"
            + "\n    liblzma-dev \\"
            + "\n    libmagick++-dev \\"
            + "\n    libopenmpi-dev \\"
            + "\n    libpcre2-dev \\"
            + "\n    libv8-dev \\"
            + "\n    libxslt1-dev \\"
            + "\n    libzmq3-dev \\"
            + "\n    qpdf \\"
            + "\n    texinfo \\"
            + "\n    software-properties-common \\"
            + "\n    vim \\"
            + "\n    libpng-dev && \\"
            + "\n    apt-get update\n\n"
        )
        return sys_deps
    
    def _dockerfile_workdir(self):
        workdir = "WORKDIR ./tugboat_dir\n\n"
        return workdir
    
    def _dockerfile_write(self):
        with open("Dockerfile", "w+") as d:
            d.write(self._dockerfile)
        with open(".dockerignore", "w+") as d:
            d.write(self._dockerignore)
        return self
    
    def _insert_software_in_config(self, software: str, version=None):
        if software.lower() in [s.lower() for s in self.requirements]:
            return self
        self.config[software] = {"version": version}
        return self
    
    def _insert_software_in_requirements(self, software: str):
        if software.lower() in [s.lower() for s in self.requirements]:
            return self
        self.requirements.append(software)
        return self
    
    def _lockfile(self):
        image_info = self._image_info()
        repository = self.repository
        image_tag = self.image_tag
        docker_inspect = subprocess.run(["docker", "inspect", (repository + ":" + image_tag)], capture_output=True)
        docker_inspect.check_returncode()
        [docker_inspect] = json.loads(docker_inspect.stdout)
        if not docker_inspect["RepoDigests"] == None:
            self.repodigest = docker_inspect["RepoDigests"]
        lockfile = {
            "Repository": self.repository,
            "ImageName": self.image_name,
            "ImageTag": self.image_tag,
            "DHUsername": self.dh_username,
            "ImageInfo": docker_inspect
        }
        lockfile_pretty = json.dumps(lockfile, indent=4)
        with open(os.path.join(self.dockerfile_dir, "gangway.lock"), "w+") as j:
            j.write(lockfile_pretty)
        return self
    
    def _software_check(self, software: list):
        if "RStudio" in software:
            self._insert_software_in_config("Quarto")
            self._insert_software_in_requirements("Quarto")
            self._insert_software_in_config("Pandoc")
            self._insert_software_in_requirements("Pandoc")
        if "Jupyter" in software:
            self._insert_software_in_config("Python")
            self._insert_software_in_requirements("Python")
        if "Quarto" in software:
            self._insert_software_in_config("Pandoc")
            self._insert_software_in_requirements("Pandoc")
        return self
    
    def _software_version(self, software: str, default=None):
        if not software in self.requirements:
            return default
        software = self.config[software]
        if not software:
            version = default
        else:
            version = software.get("version", default)
            if not version:
                version = default
        return version
    
    def dockerfile_create(self):
        print(f"Creating Dockerfile from {os.path.abspath('.')}")
        self._software_check(self.requirements)
        dockerfile = (
            self._dockerfile_prelude()
            + self._dockerfile_system_dependencies()
            + self._dockerfile_rstudio()
            + self._dockerfile_pandoc()
            + self._dockerfile_quarto()
            + self._dockerfile_julia()
            + self._dockerfile_jupyter()
            + self._dockerfile_workdir()
            + self._dockerfile_rdeps()
            + self._dockerfile_pydeps()
            + self._dockerfile_postlude()
        )
        self._dockerfile = dockerfile
        self._dockerignore = self._dockerignore_create()
        if os.path.isfile("Dockerfile"):
            with open("Dockerfile", "r") as d:
                existing_df = d.read()
        else:
            existing_df = "No Dockerfile exists"
        if not hash_text(self._dockerfile) == hash_text(existing_df):
            self._dockerfile_write()
            print(f"✅ Dockerfile has been saved at {os.path.abspath('Dockerfile')}")
            print(f"✅ .dockerignore has been saved at {os.path.abspath('.dockerignore')}")
        else:
            print("ℹ️ Dockerfile hasn't changed. Using the existing version!")
            self._using_existing_dockerfile = True
        return self

# if __name__ == "__main__":
#     test_config = TugboatConfig()
#     test_config.generate_config()
#     test_dockerfile = DockerfileGenerator(config=test_config)
#     test_dockerfile.dockerfile_create()
#     print(f"Using existing Dockerfile? {test_dockerfile._using_existing_dockerfile}")
#     print(test_dockerfile._dockerfile)
