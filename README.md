# SolarJets
Tools and scripts for working with the SolarJets zooniverse project results.   

In this README file we go through how to use this directory. This branch is meant as a condensed verison of the ramanakumars/SolarJets. This directory does not perform any of the aggegration, instead it uses the files avaliable in the catalogue uploaded under https://conservancy.umn.edu/handle/11299/257209. 

## Requirements
To install the required python modules, run the following in main repo folder:
```bash
python3 -m pip install -r requirements.txt
```

# Usage

### Download the csv and json output files from the online database.
Go to https://conservancy.umn.edu/handle/11299/257209 and download the outputs, save these under the folder exports/

### Check the data in the Data_load.ipynb notebooks
Look at the jet subjects and properties in both the csv output and json output. We introduce the Jet_clusters object and some filter options. We also introduce the MetaFile object to load the orginal fits header information.  
`Data_load.ipynb`

Look at the extracted properties of the jet clusters. Get histograms of the length, width, duration, velocity, base position and uncertainty. Possibly filter data on a maximal uncertainty. Plot the jet location on the solar map. 
`Jet_statistics.ipynb`

Visualise the final Jet clusters, get the plots and export the json or gif from subsets of jet clusters. 
`Looking_jets_plots.ipynb`