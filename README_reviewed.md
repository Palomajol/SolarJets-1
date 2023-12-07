# SolarJets
Tools and scripts for working with the SolarJets zooniverse project. Updated for the Video tool.    

In this README file we go through the workflow of this package, specifically the order in which the aggregation in run. The ipynb notebooks contained in this directory are listed with their primary function and when they can be usefull to open. 

## Requirements
To install the required python modules, run the following in main repo folder:
```bash
python3 -m pip install -r requirements.txt
```

## Aggregation 

## Getting the data
To do the aggregation, you will need the [panoptes aggregation app](https://github.com/zooniverse/aggregation-for-caesar/) installed for offline use as well as the raw classifications. See [here](https://aggregation-caesar.zooniverse.org/README.html) on how to install the aggregation tool for offline use, or follow the [installation procedure](https://github.com/ramanakumars/SolarJets/blob/main/README.md/) for the main repo to install everything.

You can download the new classifications directly from the terminal. Install the `panoptes-cli` module with pip:
```bash
pip install panoptescli
```

Configure your Zooniverse account by entering your username and password:
```bash
panoptes configure
```

First we download the project workflows, in our case number is 11265, that are in use for the current run of the project. This file will likely not change much during the different data runs, so does not always have to be downloaded again. 
```bash
panoptes project download -t workflows 11265 solar-jet-hunter-workflows.csv
```

If this is the first time the classifications will be used or the current classification data is out of date we can use the following command to generate a new classification data. Please note that generating this workflow will take some time, when it is ready it will be downloaded to your device. First we generate and download the jet or not workflow classification this has id 250559. This file should be saved in the JetOrNot/ folder.
```bash
panoptes workflow download-classifications -g 25059 JetOrNot/jet-or-not-classifications.csv
```

Similar for the box the jet workflow, which has id 21225, this file should be saved in the BoxtheJets/ folder. 
```bash
panoptes workflow download-classifications -g 21225 BoxTheJets/box-the-jets-classifications.csv
```


If the workflow does not have to be generenated we can drop the -g in both these commands.
```bash 
panoptes workflow download-classifications 25059 JetOrNot/jet-or-not-classifications.csv    

panoptes workflow download-classifications 21225 BoxTheJets/box-the-jets-classifications.csv
```


```bash
panoptes_aggregation config solar-jet-hunter-workflows.csv 25059

panoptes_aggregation config solar-jet-hunter-workflows.csv 21225
```

25059 and 21225 are the workflow ID for Jet Or Not and Box The Jets respectively. This will generate for the 2 workflows both 3 files: the extractor config, one reducer configs and the task labels. Move these files into the `configs/` folder (create the directory if it doesn't exist).

Now, to run the aggregation, call the `do_aggregration.sh` script:
```bash
scripts/do_aggregation.sh
```

which will do the following:

1. Run the extract on the `jet-or-not-classifications.csv`

2. Get and create the subject metadata summary file `solar_jet_hunter_metadata.json`

2. Trim the extracts to remove the beta test classifications

3. Run the reducer so as to get the volunteer responses for each subject

4. Get the unique jets by SOL event through clustering

5. Finally separate out and combine the question tasks of Jet Or Not and Box The Jets



## Under the hood of `do_aggregation.sh`

These are the individual components of the aggregation script:

### Getting the extracts and reduced data for Jet or Not data
Now, we can generate the extracts from the classification data by doing (in the `extracts/` directory):
```bash
cd extracts &&
panoptes_aggregation extract ../JetOrNot/jet-or-not-classifications.csv\ ../configs/Extractor_config_workflow_25059_V2.15.yaml -o jet_or_not;
```

Now, let's generate the reducted data. To do this, run (from the `reductions/` directory):
```bash
cd ../reductions
panoptes_aggregation reduce ../extracts/question_extractor_jet_or_not.csv \ ../configs/Reducer_config_workflow_25059_V2.15_question_extractor.yaml -o jet_or_not 
```
This generates the `question_reducer_jet_or_not.csv` file which contains the per-subject reduced data, which shows how many volunteers selected each answer for each subject. 

### Get the subject metadata
```bash
cd ..
panoptes project download -t subjects 11265 ../solar-jet-hunter-subjects.csv && 
python3 scripts/create_subject_metadata.py
```

This generates the `solar_jet_hunter_metadata.json` file which contains the metadata saved from the orginal fits files. 

### Getting the extracts and reduced data for Box The Jets data
Now, we can generate the extracts from the classification data by doing (in the `extracts/` directory):
```bash
cd extracts &&
panoptes_aggregation extract ../BoxTheJets/box-the-jets-classifications.csv\ ../configs/Extractor_config_workflow_21225_V50.59.yaml -o box_the_jets
```
Squash the frames to do the space aggregation
```bash
    cd ..
    python3 scripts/squash_frames.py
```

Now, let's generate the reducted data. To do this, run (from the `reductions/` directory):
```bash
cd reductions/ &&
panoptes_aggregation reduce ../extracts/shape_extractor_temporalPoint_box_the_jets_merged.csv \
    ../configs/Reducer_config_workflow_21225_V50.59_pointExtractor_temporalPoint.yaml -o box_the_jets &&

panoptes_aggregation reduce ../extracts/shape_extractor_temporalRotateRectangle_box_the_jets_merged.csv \
   ../configs/Reducer_config_workflow_21225_V50.59_shapeExtractor_temporalRotateRectangle.yaml -o box_the_jets
```

### And the questions for Box The Jet
```bash
panoptes_aggregation reduce ../extracts/question_extractor_box_the_jets.csv \ ../configs/Reducer_config_workflow_21225_V50.63_question_extractor.yaml -o box_the_jets

```

### Cluster the unique jets found per SOL event
```bash
cd .. && python3 scripts/get_unique_jets.py && python3 scripts/cluster_jets_by_sol.py
```

### Finally separate out and combine the question tasks for Jet Or Not and Box The Jets workflows
```bash
python3 scripts/process_question_tasks.py
```


