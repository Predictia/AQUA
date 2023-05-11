#!/bin/bash

#####################################################################
# Begin of user input
machine=lumi
user=padavini

# define AQUA path
if [[ -z "${AQUA}" ]]; then
  export AQUA="/users/${user}/AQUA"
  echo "AQUA path has been set to ${AQUA}"
else
  echo "AQUA path is already defined as ${AQUA}"
fi

# define installation path
export INSTALLATION_PATH="/users/${user}/mambaforge/aqua"
echo "Installation path has been set to ${INSTALLATION_PATH}"

# End of user input
#####################################################################

# change machine name in config file
sed -i "/^machine:/c\\machine: ${machine}" "${AQUA}/config/config.yaml"
echo "Machine name in config file has been set to ${machine}"

install_aqua() {
  # clean up environment
  module purge

  # load modules
  module load LUMI/22.08
  module load lumi-container-wrapper

  mkdir -p ${INSTALLATION_PATH}  
  conda-containerize new --mamba --prefix "${INSTALLATION_PATH}" "${AQUA}/config/machines/lumi/installation/environment_lumi.yml"
  conda-containerize update "${INSTALLATION_PATH}" --post-install "${AQUA}/config/machines/lumi/installation/pip_lumi.txt"
  echo "AQUA has been installed."
}

# if INSTALLATION_PATH does not exist, create it
if [[ ! -d "${INSTALLATION_PATH}" ]]; then
  mkdir -p "${INSTALLATION_PATH}"
  echo "Installation path ${INSTALLATION_PATH} has been created."
else
  echo "Installation path ${INSTALLATION_PATH} already exists."
fi

# if INSTALLATION_PATH is empty, install AQUA
if [[ -z "$(ls -A ${INSTALLATION_PATH})" ]]; then
  echo "Installing AQUA..."
  # install AQUA
  install_aqua
  echo "AQUA has been installed."
else
  echo "AQUA is already installed."
  # check if reinstallation is wanted
  read -p "Do you want to reinstall AQUA? (y/n) " -n 1 -r
  echo # move to a new line
  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    # run code to reinstall AQUA
    echo "Removing AQUA..."
    read -p "Are you sure you want to delete ${INSTALLATION_PATH}? (y/n) " -n 1 -r
    echo # move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
      rm -rf "${INSTALLATION_PATH}"
    else
      echo "Deletion cancelled."
      return 1
    fi
    echo "Installing AQUA..."
    install_aqua
    echo "AQUA has been installed."
  else
    echo "AQUA will not be reinstalled."
  fi
fi

# load conda environment
export PATH="${INSTALLATION_PATH}/bin:$PATH"
echo "AQUA environment loaded."

# check if the line is already present in the .bashrc file
if ! grep -q "export PATH=\"\${INSTALLATION_PATH}/bin:\$PATH\"" ~/.bashrc; then
  # if not, append it to the end of the file
  echo "export PATH=\"\${INSTALLATION_PATH}/bin:\$PATH\"" >> ~/.bashrc
  echo "export PATH has been added to .bashrc."
else
  echo "export PATH is already present in .bashrc."
fi
