# Converting CSV to GeoJSON

[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen)](https://lbesson.mit-license.org/)
![Python](https://img.shields.io/badge/language-Python-brightgreen)
![Version](https://img.shields.io/badge/python-3.6%20%7C%203.7-blue)


## Overview

A simple application built with [Flask](https://flask.palletsprojects.com/en/1.1.x/) and [Vanilla JavaScript](http://vanilla-js.com/) for converting [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) table to GeoJSON code. The code is ready for use in MediaWiki extension [Kartographer](https://www.mediawiki.org/wiki/Extension:Kartographer), which add map capability to the Wikipedia pages.

## Features

- Converting CSV table to GeoJSON code
- Showing data on an HTML table preview
- Preview of the coordinates on a Leaflet map
- Beautify and minimize GeoJSON code
- Automatically adding color and icon to the GeoJSON markers

## Built With

- Flesk
- Jinja2
- Vanilla JavaScript
- Bootstrap
- Leaflet

## Usage
The first step is to go to [Wikidata Query Service](https://query.wikidata.org/) and prepare a SPARQL query similar to 

```SPARQL
SELECT DISTINCT ?item ?itemLabel ?page_title ?image ?coordinate_location WHERE {

  ?item (wdt:P31/(wdt:P279*)) wd:Q2232001; 
         wdt:P17 wd:Q219.
         
  ?article schema:about ?item; 
           schema:isPartOf <https://bg.wikipedia.org/>;  
           schema:name ?page_title .
           
  ?item rdfs:label ?LabelBG filter (lang(?LabelBG) = "bg") .
  
  OPTIONAL { ?item wdt:P18 ?image. }
  OPTIONAL { ?item wdt:P625 ?coordinate_location. }
  
  MINUS { ?item wdt:P576 _:b1. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "bg". }
  
}ORDER BY (?itemLabel)
```
The columns must be named: **item | itemLabel | page_title | image | coordinate_location** and when the date is ready for use is exported to CSV file.

The second step is to go to [this](https://csvtojsonconverting.herokuapp.com/) website, upload the file and pick the color and icon for the markers.

