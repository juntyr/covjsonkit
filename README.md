| :warning: This project is BETA and will be experimental for the foreseeable future. Interfaces and functionality are likely to change. DO NOT use this software in any project/software that is operational. |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

## covjsonkit

<p align="center">
  <a href="https://github.com/ecmwf/polytope/actions/workflows/ci.yaml">
  <img src="https://github.com/ecmwf/polytope/actions/workflows/ci.yaml/badge.svg" alt="ci">
</a>
  <a href="https://codecov.io/gh/ecmwf/polytope"><img src="https://codecov.io/gh/ecmwf/polytope/branch/develop/graph/badge.svg"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"></a>
  <a href="https://github.com/ecmwf/polytope/releases"><img src="https://img.shields.io/github/v/release/ecmwf/polytope?color=blue&label=Release&style=flat-square"></a>
  <a href='https://polytope.readthedocs.io/en/latest/?badge=latest'><img src='https://readthedocs.org/projects/polytope/badge/?version=latest' alt='Documentation Status' /></a>
</p>
<p align="center">
  <a href="#concept">Concept</a> •
  <a href="#installation">Installation</a> •
  <a href="#example">Example</a> •
  <a href="#testing">Testing</a> •
  <a href="https://polytope.readthedocs.io/en/latest/">Documentation</a>
</p>

ECMWF library for encoding and decoding coverageJSON files/objects of meteorlogical features such as vertical profiles and time series.

* Encodes and decodes CoverageJSON objects
* Convert CoverageJSON files to and from xarray

Current features implemented:

* Time Series
* Vertical Profile
* Bounding Box
* Frame
* Path