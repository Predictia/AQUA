.. _faq_installation:
I am getting an error when trying to install AQUA on LUMI
=========================================================

It is possible that, if you're recreating the environment, the code breaks while removing the folder ``~/mambaforge/aqua/bin``, complaining the resource is busy.
In this case you may have some processes running in the background. 
You can check them with ``ps -ef | grep aqua | grep $USER``. and kill them manually if needed.