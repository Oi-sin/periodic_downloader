# Periodic downloader
Simple python script for downloading data from an URL in fixed intervals and save it to a file.

## What problem does it solve
Download data from an URL in regular intervals, eg. JSON from an open data site for further investigation. Based on a configuration file `tasks.json` the data from the URL is downloaded to a configurable directory. The file name can be timestamped using python formatting syntax. The downloaded data is only saved to file if its content has changed. This is accomplished by remembering hash value of data for each URL.

## Requirements
This project has been created using Python 3.8. The `requests` package is required.

## How to use
Create and fill the configuration file `tasks.json` with the URL and folder information for the download. This file may be based on the template file `tasks.json.template`. Then execute then `run.py` script. This script is thought to  be called automatically by `cron`.

## Configuration file
The project includes a template `tasks.json.template`. It should be renamed to `tasks.json`. 

The file contains a list of tasks. Each task has the following parameters

### Name
Just some text to describe the task for better orientation. It is not used anywhere except debug messages.

### URL
URL to download data from. This URL must publicly available (i.e. require no login credentials or session cookies).

### Interval
The interval can be given either in minutes `m` from 1 to 60 or in hours `h` from 1 to 24. 

### TargetFilename
Gives the file name for the downloaded data. This may included python formatted timestamp information such as date and time.

### TargetDir
Gives the directory for the downloaded data. This may included python formatted timestamp information such as date and time (Alert: but only if not `TempDir` is used). This may be an absolute path or a path relative to the `tasks.json` file.

### TempDir
Gives a directory to store the downloaded data locally before moving it to the target directory. This may be an absolute path or a path relative to the `tasks.json` file. This might be useful if the target directory is on a remote system such as a NAS that might be temporary unavailable. Data is moved to the target directory the next time the system is available.

### Sample file
```JSON
{"Tasks": 
    [{
        "Name": "Free apointments in the vaccination centers in Saxony",
        "URL": "https://www.startupuniverse.ch/api/1.1/de/counters/getAll/_iz_sachsen",
        "Interval": "10m",
        "TargetFilename": "%Y%m%d_%H%M.json",
        "TargetDir": "/mnt/nas/data/covid_saxony",
        "TempDir": "__tempdata\\"
    },
    {
        "Name": "Daily file with covid cases for the city of Dresden",
        "URL": "http://opendata.dresden.de/duva2ckan/files/de-sn-dresden-corona_-_covid-19_-_fallzahlen_md1_dresden_2020ff/content",
        "Interval": "24h",
        "TempTargetFilename": "Covid_dd_cases_%Y%m%d.csv",
        "TargetDir": "/mnt/nas/data/covid_dd/%Y%m",
        "TempDir": ""
    }]
}
```

## TODO / Known bugs
- timestamping target directory does not work, if a temp directory is used.
- better error handling if download fails