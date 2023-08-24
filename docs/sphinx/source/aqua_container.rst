AQUA Container
==============

Using a Singularity container, you can quickly load the AQUA environment on platforms like LUMI, Marenostrum, or Levante. This guide explains how to use the AQUA environment using the container, with a focus on LUMI. However, the same instructions apply to Marenostrum 4 and Levante.

.. contents::
   :local:
   :depth: 2

Load AQUA Environment into the Shell
-------------------------------------

1. Create a shell script named "load_aqua" using the following code:

.. code-block:: bash

   cat << 'EOF' > load_aqua
   #!/bin/bash

   AQUA_container="/project/project_465000454/containers/aqua/aqua-v0.2.sif"
   FDB5_CONFIG_FILE="/scratch/project_465000454/igonzalez/fdb-long/config.yaml"
   GSV_WEIGHTS_PATH="/scratch/project_465000454/igonzalez/gsv_weights/"
   GRID_DEFINITION_PATH="/scratch/project_465000454/igonzalez/grid_definitions"

   singularity shell \
       --cleanenv \
       --env FDB5_CONFIG_FILE=$FDB5_CONFIG_FILE \
       --env GSV_WEIGHTS_PATH=$GSV_WEIGHTS_PATH \
       --env GRID_DEFINITION_PATH=$GRID_DEFINITION_PATH \
       --env ESMFMKFILE=/opt/conda/lib/esmf.mk \
       --bind /pfs/lustrep3/scratch/project_465000454 \
       --bind /scratch/project_465000454 \
       $AQUA_container
   EOF

   chmod +x load_aqua

2. Run the following code to load the AQUA environment into the shell:

.. code-block:: bash

   ./load_aqua

Running Jupyter Notebook
------------------------

To run a Jupyter Notebook using the AQUA environment, follow these steps. Note that if you want to run Jupyter Notebook within VS Code, execute these steps inside VS Code.

1. Run the previously saved script in the terminal to load the AQUA Singularity container into the shell:

.. code-block:: bash

   ./load_aqua

2. Start Jupyter Lab, which will provide a server URL like: http://localhost:8888/lab?token=random_token.

.. code-block:: bash

   jupyter-lab --port=8888 --no-browser

3. Skip 3 and 4 step if you want to open notebook in VS-code.
If you wish to open Jupyter Lab in your browser, execute the following command in a separate terminal, replacing "lumi" with your SSH hostname:

.. code-block:: bash

   ssh -L 8888:localhost:8888 lumi

4. Open the Jupyter Lab URL in your browser. It will launch Jupyter Lab. Choose the "Python 3 (ipykernel)" kernel for the AQUA environment.

5. For opening notebooks in VS Code, copy the Jupyter server URL.

6. Open a notebook in VS Code and in the top-right corner of the notebook, click on "Select kernel" >> "Select another kernel" >> "Existing Jupyter server" >> "Enter the URL" and paste the copied Jupyter server URL, then press enter.

7. Select "Python 3 (ipykernel)" as the kernel for the AQUA environment.

That's it! You can now work within the AQUA environment using Jupyter Notebook.
