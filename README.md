# Digital Twin of Society

This repository provides an implementation of a prototype web-based Digital Twin for societal geographic data, which includes functionalities for visualizing and forecasting.

## Overview

![](./dtsociety_arch.png)

### Frontend

- Visualisation of data and forecasts (plotly)

### Backend

- Processing, transformation and filtering of data (Pandas, NumPy)
- Fitting of and predictions of forecasting models (scikit-learn, statsmodels, FB Prophet)

### Database

- Persistence of datasets provided by the user (MongoDB)

## Setup

### Requirements

- Angular 14.2.5
- Anaconda
- Python 3.10
- MongoDB 6.0

### Conda environment + backend

After installing Anaconda you can setup the Python environment for the backend with:

`$ conda env create -f app/environment.yml`

Once the environment has been configured successfully, you can start the backend.  
`$ cd app/flask `  
`$ flask --app flaskr --debug run`

### Database connection

The backend will automatically create a new collection at the default location:  
`mongodb://127.0.0.1:27017/dt_society_datasets`

### Starting the application

If all requirements have been successfully installed you can start the frontend on a local development server (port 4200 as default) with the Angular CLI:  
`$ cd app/angular`  
`$ ng serve --open`

## Application usage

### File upload

Currently the application supports `.tsv` and `.csv` datasets, which contain a column with country codes. You must specify the appropriate separator before uploading your dataset.

### Data filtering

All 4 dropdowns must be selected in order to provide visualisations. These include:

- Column with country codes (geo)
- Column with timestamps (x)
- Columns with feature of interest (y)

The reshape dropdown is optional and only necessary if your dataset has a wide format, i.e. each timestamp represents a column. Select N/A if this does not apply to your dataset.

### Forecasting

You can choose between multivariate and scenario-based forecasting.  
Multivariate forecasting performs a forecast for each selected feature simultaneously while taking correlations into account.  
Scenario-based forecasting allows you to perform a forecast for a selected feature based on artificial scenarios for each other feature, which you can specify.  
Both of these methods can forecast up to 40 future timesteps. However, all features provided in the datasets must have the same underlying time frequency. (i.e. all timestamps must be yearly)
