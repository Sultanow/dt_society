# Digital Twin of Society in Dash

## Environment

Run command to setup the conda environment

`$ conda env create -f environment.yml`

## Dash app

After the environment is installed successfully you can start the dash app.

`$ python app.py`

You can access the application in your browser at `127.0.0.1:8050`.

## Uploading files

Currently you are able to upload CSV and TSV files. However, it is required to specify the seperator beforehand.  
After successfully uploading a dataset you can select the columns of interest for each required dropdown.

## Demo mode

The demo mode can be used by pressing the DEMO button located in the files section. For the seperator, you have to select the `\t` seperator  
from the dropdown before pressing the DEMO button.

## Reshaping data

The most common format for time series has a row of data for each observation and a column for each observed feature.  
If you are dealing with datasets similar to datasets provided by EuroStat (rows indicate observed feature, columns indicate observation),  
you must use the reshape function. Here you should select the column that contains all of the observed features.  