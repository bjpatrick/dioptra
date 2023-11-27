# Tensorflow MNIST Pixel Threshold Demo (legacy)

The demo provided in the Jupyter notebook file [demo.ipynb](demo.ipynb) uses Dioptra to run experiments that investigate the effects of the pixel threshold attack when launched on a neural network model trained on the MNIST dataset.

## Running the example

To prepare your environment for running this example, follow the linked instructions below:

1.  [Create and activate a Python virtual environment and install the necessary dependencies](../README.md#creating-a-virtual-environment)
2.  [Download the MNIST dataset using the download_data.py script.](../README.md#downloading-datasets)
3.  [Follow the links in these User Setup instructions](../../README.md#user-setup) to do the following:
    -   Build the containers
    -   Use the cookiecutter template to generate the scripts, configuration files, and Docker Compose files you will need to run Dioptra
4.  [Edit the docker-compose.yml file to mount the data folder in the worker containers](../README.md#mounting-the-data-folder-in-the-worker-containers)
5.  [Initialize and start Dioptra](https://pages.nist.gov/dioptra/getting-started/running-dioptra.html#initializing-the-deployment)
6.  [Register the custom task plugins for Dioptra's examples and demos](../README.md#registering-custom-task-plugins)
7.  [Register the queues for Dioptra's examples and demos](../README.md#registering-queues)
8.  [Start JupyterLab and open `demo.ipynb`](../README.md#starting-jupyter-lab)

Steps 1–4 and 6–7 only need to be run once.
**Returning users only need to repeat Steps 5 (if you stopped Dioptra using `docker compose down`) and 8 (if you stopped the `jupyter lab` process)**.