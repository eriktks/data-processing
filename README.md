Data Processing (What Works When for Whom?)
===========================================

[![DOI](https://zenodo.org/badge/129427565.svg)](https://zenodo.org/badge/latestdoi/129427565)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)
[![Research Software Directory](https://img.shields.io/badge/rsd-Research%20Software%20Directory-00a3e3.svg)](https://www.research-software.nl/software/dataprocessing)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=e-mental-health_data-processing&metric=alert_status)](https://sonarcloud.io/dashboard?id=e-mental-health_data-processing)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c8919c12df0e4c548e7bcff3d55818ae)](https://www.codacy.com/manual/eriktks/data-processing_2?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=e-mental-health/data-processing&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/fbc09669dbc8c0449e0e/maintainability)](https://codeclimate.com/github/e-mental-health/data-processing/maintainability)

Data processing scripts of the e-Mental Health project. The scripts deal with two data sets: OVK and Tactus

OVK mails
---------

The OVK data consist of Word files with e-mails. First, each Word file was converted to text:
```
abiword -t text 1234.docx # creates file 1234.text
```

Next, extra lines have been added to the text files to indicate where a new email started. A typical separator line was "Date: 1 Jan 2000":
```
ovkPrepare.py 1234.text > 1234.prepared # expects a numeric file name
```
The program tries to guess the author of an email but this sometimes fails. The missed names are indicated by the string "???" and need to be added manually.

The files contain personal information, which needs to be removed. Therefore all names and numbers were removed from the file. This process contains two steps: 1. named entity recognition (ner), and 2. anonymization:
```
ner.py < 1234.prepared > 1234.ner # requires frog, see comment below
anonymize.py 1234.ner             # creates file 1234.ner.out, see comment below
```

For named entity recognition, we rely the program `frog`, which is part of the [LaMachine](https://github.com/proycon/lamachine) package. After installing the package, we run it as follows:
```
docker run -p 8080:8080 -t -i proycon/lamachine
lamachine@abcd1234:/$ frog -S 8080 --skip mcpla
```
After starting LaMachine like this, the `ner.py` program is able to process the texts.

The anonymization process (`anonymize.py`) is interactive. Each new entity will be displayed on the screen and the user is required to enter the entity type (like PER, ORG or LOC) or an empty string (which stands for: no entity).

In the file `1234.ner.out`, all names and numbers have been replaced by dummy strings (like PER for person names). Mail headers signalling the start of a new mail, start on a new line containing a capitalized word followed by a space and a colon (like: "Date :"). All other lines contain a single sentence.

Finally, the output files of the anonymization process can be converted to a csv table which can be used for analysis:
```
ovk2table.py 1234.ner.out ... > all.csv
```
The program `ovk2table.py` assumes that the files contain emails in chronological order. The local file `reversed.txt` contains the names of files with the emails in reversed chronological order.

The Jupyter notebooks `pca.ipynb` and `pca-results.ipynb` can be used for analyzing the data in the csv tables. `pca.ipynb` uses principle-component analysis for visualizing the e-mails on a two-dimensional space. It also displays words which are specific for subsets of the emails. `pca-results.ipynb` performs exactly the same task but next to building models from the words in the emails, it also displays information on the treatment progress.

Tactus mails
------------

The Tactus data consist of XML files with emails. These can be converted to csv table:
```
tactus2table.py 1234.xml ... # creates file ../output/emails.csv
```

The texts of the mails need to be anonymized. There is no automatic solution for this yet.

The data in the csv table can be analysed with the Jupyter notebooks `pca-tactus.ipynb` and `pca-tactus-results.ipynb`, in the same way as the OVK data.

Metadata
--------

The OVK metadata is stored in the SPSS file `opve.sav`. The file was converted to csv with R:
```
library(foreign)
data <- read.spss("file.sav")
write.csv(data,file="file.csv")
```
The Tactus metadata is stored in the XML file of each client. The program `tactus2table.py` extracts these and stores them in five files in the directory `../output` (`Intake.csv` and `Lijst.*`)


Installation
------------
clone the repository  
```
git clone git@github.com:eriktks/data-processing.git
```
change into the top-level directory  
```
cd data-processing
```

Dependencies
------------
 * Python 3.6

License
-------
Copyright (c) 2018, Erik Tjong Kim Sang

Apache Software License 2.0

Contributing
------------
Contributing authors so far:
* Erik Tjong Kim Sang

# Information added by Python template

## Badges

(Customize these badges with your own links, and check https://shields.io/ or https://badgen.net/ to see which other badges are available.)

| fair-software.eu recommendations | |
| :-- | :--  |
| (1/5) code repository              | [![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/e-mental-health/data-processing) |
| (2/5) license                      | [![github license badge](https://img.shields.io/github/license/e-mental-health/data-processing)](https://github.com/e-mental-health/data-processing) |
| (3/5) community registry           | [![RSD](https://img.shields.io/badge/rsd-data-processing-00a3e3.svg)](https://www.research-software.nl/software/data-processing) [![workflow pypi badge](https://img.shields.io/pypi/v/data-processing.svg?colorB=blue)](https://pypi.python.org/project/data-processing/) |
| (4/5) citation                     | [![DOI](https://zenodo.org/badge/DOI/<replace-with-created-DOI>.svg)](https://doi.org/<replace-with-created-DOI>) |
| (5/5) checklist                    | [![workflow cii badge](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>/badge)](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>) |
| howfairis                          | [![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu) |
| **Other best practices**           | &nbsp; |
| Static analysis                    | [![workflow scq badge](https://sonarcloud.io/api/project_badges/measure?project=e-mental-health_data-processing&metric=alert_status)](https://sonarcloud.io/dashboard?id=e-mental-health_data-processing) |
| Coverage                           | [![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=e-mental-health_data-processing&metric=coverage)](https://sonarcloud.io/dashboard?id=e-mental-health_data-processing) |
| Documentation                      | [![Documentation Status](https://readthedocs.org/projects/data-processing/badge/?version=latest)](https://data-processing.readthedocs.io/en/latest/?badge=latest) |
| **GitHub Actions**                 | &nbsp; |
| Build                              | [![build](https://github.com/e-mental-health/data-processing/actions/workflows/build.yml/badge.svg)](https://github.com/e-mental-health/data-processing/actions/workflows/build.yml) |
|  Metadata consistency              | [![cffconvert](https://github.com/e-mental-health/data-processing/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/e-mental-health/data-processing/actions/workflows/cffconvert.yml) |
| Lint                               | [![lint](https://github.com/e-mental-health/data-processing/actions/workflows/lint.yml/badge.svg)](https://github.com/e-mental-health/data-processing/actions/workflows/lint.yml) |
| SonarCloud                         | [![sonarcloud](https://github.com/e-mental-health/data-processing/actions/workflows/sonarcloud.yml/badge.svg)](https://github.com/e-mental-health/data-processing/actions/workflows/sonarcloud.yml) |
| MarkDown link checker              | [![markdown-link-check](https://github.com/e-mental-health/data-processing/actions/workflows/markdown-link-check.yml/badge.svg)](https://github.com/e-mental-health/data-processing/actions/workflows/markdown-link-check.yml) |

## How to use data_processing



The project setup is documented in [project_setup.md](project_setup.md). Feel free to remove this document (and/or the link to this document) if you don't need it.

## Installation

To install data_processing from GitHub repository, do:

```console
git clone https://github.com/e-mental-health/data-processing.git
cd data-processing
python3 -m pip install .
```

## Documentation

Include a link to your project's full documentation here.

## Contributing

If you want to contribute to the development of data-processing,
have a look at the [contribution guidelines](CONTRIBUTING.md).

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
