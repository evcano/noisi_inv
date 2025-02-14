## Noisi - ambient noise cross-correlation modeling and inversion

This tool can be used to simulate noise cross-correlations and sensitivity kernels to noise sources.

### Installation

Install requirements (easiest done with anaconda)
- [obspy](https://docs.obspy.org/)
- PyYaml
- pandas
- mpi4py
- geographiclib
- cartopy
- h5py
- jupyter
- pytest
- pyasdf
- psutil

Additionally, install [instaseis](http://instaseis.net/), if you plan to use it for Green's functions (`pip install instaseis`). Currently it requires Python <= 3.8.

Install jupyter notebook if you intend to run the tutorial (see below).

If you encounter problems with mpi4py, try removing it and reinstalling it using pip (`pip install mpi4py`).

Clone the repository with git:
`git clone https://github.com/jigel/noisi_inv.git`

Change into the `noisi/` directory. Call `pip install .` here, or call `pip install -v -e .` if you intend to modify the code.

After installation, change to the `noisi/noisi` directory and run `pytest`. If you encounter any errors (warnings are o.k.), we'll be grateful if you let us know. 

### Getting started
To see an overview of the tool, type `noisi --help`.
A step-by-step tutorial for jupyter notebook can be found in the `noisi/noisi` directory.
Examples on how to set up an inversion and how to import a wavefield from axisem3d are found in the noisi/examples directory.

### Tutorial: Inversion setup
We have added a jupyter notebook to help you setup a config file for an inversion. All the different parameters are explained within that notebook. It is also available as python script. 

It is recommended to download a pre-computed wavefield if you want to do proper inversions (http://ds.iris.edu/ds/products/syngine/). These are then easily implemented in the config file. 


