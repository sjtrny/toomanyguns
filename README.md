[![Build Status](https://travis-ci.org/sjtrny/toomanyguns.svg?branch=master)](https://travis-ci.org/sjtrny/toomanyguns)

# toomanyguns

A plotly dash app displaying ownership of firearms in NSW, Australia.

## Live Demo

https://toomanyguns.render.com/

## Screenshot

<img src="https://github.com/sjtrny/toomanyguns/raw/master/screenshots/example.png" height="480">

## How?

With a combination of:

- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), to parse the original [website](http://toomanyguns.herokuapp.com/)
- [GeoPandas](http://geopandas.org/), for geographic pre-processing
- [Dash](https://github.com/plotly/dash), for creating the website
- [Mapbox](https://www.mapbox.com/), for interactive maps

With dash we use a few notable features, techniques and third-party libraries:
- [dash-bootstrap-components](https://github.com/facultyai/dash-bootstrap-components), to make pages responsive and pretty
- [client side callbacks](https://dash.plot.ly/performance), for network performance reasons
- [store component](https://dash.plot.ly/dash-core-components/store), for network performance reasons
- [bs-breakpoints](https://github.com/Johann-S/bs-breakpoints), to tweak layout for different breakpoints

## Data Sources

##### Postcode Information

Sourced from [https://www.matthewproctor.com/australian_postcodes](https://www.matthewproctor.com/australian_postcodes)

##### Postal Area Geography Data

This information is available from the ABS under the listing [1270.0.55.003 - Australian Statistical Geography Standard (ASGS): Volume 3 - Non ABS Structures, July 2016](https://www.abs.gov.au/AUSSTATS/abs@.nsf/DetailsPage/1270.0.55.003July%202016?OpenDocument)

The specific file used is titled "Postal Areas ASGS Ed 2016 Digital Boundaries in ESRI Shapefile Format"

##### Firearms Data

We did our best to scrape [http://toomanyguns.org](http://toomanyguns.org).

[Click here to download it](https://raw.githubusercontent.com/sjtrny/toomanyguns/master/assets/firearms_2019.csv).
