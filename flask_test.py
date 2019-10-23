import os
import sys
import pandas
import re
import json
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import urllib.parse


ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	return render_template("upload_file.html")
	
@app.route('/error')
def error():
	return render_template("error.html")
	
@app.route('/error_col')
def error_col():
	return render_template("error_col.html")
	

@app.route('/csv_to_geojson', methods=['POST'])  
def csv_text():
	color = request.form.get('color')
	color=color.replace("#","")
	icon = request.form.get('icon')

	if icon=="Choose icon type":
		icon='marker'

	if request.method == 'POST': 
		if 'file' not in request.files:
			return redirect(url_for('error'))

		file = request.files['file']

		if file.filename == '':
			return redirect(url_for('error'))
		
		# check if this file is allowed type
		if file and allowed_file(file.filename):
			df=pandas.read_csv(file, delimiter=',')

			# check if the names of columns are valid
			if not {'item', 'itemLabel','page_title','image','coordinate_location'}.issubset(df.columns):
				return redirect(url_for('error_col'))

			# check if coordinates are differente than NaN
			for coor in range(len(df["item"])):
				if pandas.isnull(df.at[coor, 'coordinate_location']):
					df=df.drop(coor)
			
			df=df.reset_index(drop=True)
			
			
			length=len(df["item"].values.tolist())	

			itemArray=df["item"].values.tolist()
			itemNameArray=[]
			
			imageArray=df["image"].values.tolist()
			imageNameArray=[]
			
			pageName=df["page_title"].values.tolist()
			
			latitude=[]
			longitude=[]
			
			for i in range(length):
				imageArray[i]=str(imageArray[i])
				pageName[i]=str(pageName[i])
				
				imageName = Path(urllib.parse.unquote(imageArray[i]))
				if str(imageName)!='nan':
					imageNameArray.append(imageName.parts[4])
				else:
					imageNameArray.append("")
						
				itemName = Path(urllib.parse.unquote(itemArray[0]))
				itemNameArray.append(itemName.parts[3])
				
				# converting coordinate_location
				text=df.at[i,'coordinate_location'].replace("Point(","").replace(")","")
				x = re.split("\s", text)
				latitude.append(x[0])
				longitude.append(x[1])

			df['Latitude'] = latitude
			df['Longitude'] = longitude
			
			# mean value of coordinates 
			lat=df['Latitude'].astype(float)
			lon=df['Longitude'].astype(float)
			latMean=lat.mean()
			lonMean=lon.mean()
			
			# creating geojson
			text_json=''
			comma=',\n'
			description=''
			title=''
			
			for i in range(length):
				if i == length-1:
					comma=''
					
				if imageNameArray[i]!='':
					description="[[Файл:"+str(imageNameArray[i])+"|280px]]"
				else:
					description=''
					
				if (pageName[i]==str(df.at[i,'itemLabel'])) or (pageName[i]=="nan"):
					title="[["+df.at[i,'itemLabel']+"]]"
				else:
					title="[["+str(pageName[i])+"""|"""+df.at[i,'itemLabel']+"]]"
		
					
				item="""{
						"type": "Feature",
						"properties": {
							"title": \""""+title+"""\",
							"description": \""""+description+"""\",
							"marker-symbol": \""""+icon+"""\",
							"marker-size": "medium",
							"marker-color": \""""+color+"""\"
						  },
						  "geometry": {
							"type": "Point",
							"coordinates": ["""+df.at[i,'Latitude']+""", """+df.at[i,'Longitude']+"""]
						  }
					}"""+comma
				
				text_json+=item

			message="""{
						"type": "FeatureCollection",
						"features": [\n"""+text_json+"""\n  ]\n
					}"""
			
			
			# creating geojson for map preview
			text_json_map=''
			comma=',\n'
			descriptionMap=''
			
			for i in range(length):
				if i == length-1:
					comma=''
					
				if imageNameArray[i]!='':
					descriptionMap="http://commons.wikimedia.org/wiki/Special:FilePath/"+str(imageNameArray[i])
				else:
					descriptionMap=''
						
					
				itemMap="""{
						"type": "Feature",
						"properties": {
							"title": \""""+df.at[i,'itemLabel']+"""\",
							"description": \""""+descriptionMap+"""\"
						  },
						  "geometry": {
							"type": "Point",
							"coordinates": ["""+df.at[i,'Latitude']+""", """+df.at[i,'Longitude']+"""]
						  }
					}"""+comma
				
				text_json_map+=itemMap

			messageMap="""{
						"type": "FeatureCollection",
						"features": [\n"""+text_json_map+"""\n  ]\n
					}"""
			
			return render_template("csv_text.html", name = file.filename, item=itemArray, itemName=itemNameArray, itemLabel=df["itemLabel"].values.tolist(), image=imageArray, latitude=df["Latitude"].values.tolist(), longitude=df["Longitude"].values.tolist(), page=pageName, len = length, json_text=message, json_map=messageMap, latMean=latMean, lonMean=lonMean)
		
		return redirect(url_for('index'))

if __name__ == '__main__':
	app.run()
