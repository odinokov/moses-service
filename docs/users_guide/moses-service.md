[issue-template]: ../../../../../issues/new?template=BUG_REPORT.md
[feature-template]: ../../../../../issues/new?template=FEATURE_REQUEST.md

![singnetlogo](../assets/singnet-logo.jpg?raw=true 'SingularityNET')

# Mozi Moses Service


This service uses the OpenCog meta optimising semantic evolutionary search algorithm [MOSES](https://github.com/opencog/moses)
to generate a supervised binary classification model of genomic or other high dimensional binary feature data sets using boolean regression..

It is part of a set of SingularityNET demonstration bio AI agents adapted from [Mozi.AI](https://mozi.ai) suite of OpenCog based bioinformatics tools.

### Data


Data set with binary values, observations in rows, features in columns, observation labels assumed in first column unless specified with parameter flag.

For genomic data, variants are naturally represented with a "one" value when present in a sample.  For diploid samples a "dominant" model can be used with a "one" for heterozygous or homozygous for the variant, a "recessive" model with a "one" for homozygous variant only, or by using two features for each variant, one for each possiblility.

For numerically valued features such as transcript of protein levels, the median norm can be used where an observation is coded "one" if it is greater than the median value for the feature across all observations.

## Getting Started


### Requirements

- [Python 3.6.5](https://www.python.org/downloads/release/python-365/)
- [Node 8+ w/npm](https://nodejs.org/en/download/)



### Development

Clone this repository:

```
$ git clone https://github.com/Habush/moses-service.git

$ cd mozi_snet_service
```

### Calling the service:


a. Install the `mozi-cli` python tool for generating the query.json file used to call the file

```
$ pip install mozi-cli

$ mozi-cli [dataset-file] [path-to-save-output]
```
Look at the documentation for mozi-cli [here](https://github.com/Habush/mozi-service-cli)


b. Assuming that you have an open channel (`id: 0`) to this service use the generated **query.json** file to call the service

```
$ snet client call 0 0.00000001 46.4.115.181:5002 StartAnalysis query.json
...
response: 
INFO - resultUrl: "http://46.4.115.181:8080/?id=<session-id>"
description: "Analysis started"
```

*Note:* you can use this service through the [SingularityNET DApp](beta.singularitynet.io)


## Contributing and Reporting Issues

Please read our [guidelines](https://github.com/singnet/wiki/blob/master/guidelines/CONTRIBUTING.md#submitting-an-issue) before submitting an issue.
If your issue is a bug, please use the bug template pre-populated [here][issue-template].
For feature requests and queries you can use [this template][feature-template].

## Authors

* **Abdulrahman Semrie** - *xabush@singularity.io*
* **Yisehak Abreham** - *abrehamy@singularitynet.io* 

<i class="fa fa-copyright"/> 2019 [SingularityNET](https://www.singularitynet.io)