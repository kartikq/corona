# COVID-19 CLI

This package provides a command line interface for presenting current COVID-19 statistics. 
Data is sourced from Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE). 
Also, Supported by ESRI Living Atlas Team and the Johns Hopkins University Applied Physics Lab (JHU APL).
https://systems.jhu.edu/research/public-health/ncov/
## Usage
```
Usage: corona.py [OPTIONS]

  Command line interface for COVID-19 statistics. Data sourced from Johns
  Hopkins University Center for Systems Science and Engineering (JHU CSSE).
  Also, Supported by ESRI Living Atlas Team and the Johns Hopkins University
  Applied Physics Lab (JHU APL).

Options:
  --country TEXT  filter by country
  --region TEXT   filter by region (requires country)
  --summary       print summary statistics
  --date TEXT     filter by date YYYY-MM-DD
  --help          Show this message and exit.
```

## Installation

```bash
$ git clone https://github.com/kartikq/corona.git 

$ git submodule init

$ git submodule update

$ pip install -r requirements.txt
```