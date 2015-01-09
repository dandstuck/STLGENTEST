import os
import re
import json
from flask import Flask, request, render_template, send_file

from DestinyModel import DestinyModel 

app = Flask(__name__)

outputPath = "stl/"

@app.route('/')
def welcome():
    # Load gear JSON file
    f = open("./gear/gear.json", 'r')
    gear = json.loads(f.read())
    f.close()
        
    return render_template('welcome.html', gear=gear)
    
@app.route('/contact')
def contact():
    return render_template('contact.html') 
    
@app.route('/download', methods=['GET'])
def download():
    # Parse the arguments for item name and generate the key
    item = request.args.get('item')
    key = re.sub(r'[^a-zA-Z0-9 ]', '', item).lower()
    
    # Create stl file name and path
    fileName = key.replace(" ","_")+".stl"
    filePath = outputPath+fileName
    
    # Create output directory
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    
    # Check if file has already been created
    if os.path.exists(filePath):
        print("Using existing file "+filePath)
        # Read in the file contents
        with open(filePath, 'r') as fi:
            output = fi.read()
            fi.close()
    else:
        # Load gear JSON file
        f = open("./gear/gear.json", 'r')
        gear = json.loads(f.read())
        f.close()
        
        # Download the model data for this item
        try:
            # Download the model geometries
            print("Loading model with key "+key+"...")
            model = DestinyModel(item, gear[key]["json"])
            
            # Generate the output
            print("Generating output...")
            output = model.generate()
            
            # Write output file
            with open(filePath, 'w') as fo:
                fo.write(output)
                fo.close()
            print("Wrote output file "+filePath)
        except:
            output = "Unable to generate files for item: "+str(item)
            return render_template('output.html', output=output)
            # error page
            
    # Return the file download page
    return render_template('download.html', item=item, fileName=fileName, filePath=filePath, output=output)

@app.route('/stl/<path:filename>')
def send_tmp_file(filename):
    try:
        if ".." in filename:
           return "Error retrieving file"
        else:
            path = outputPath+filename
            print("Sending",path)
            return send_file(path)
    except:
       return "Error retrieving file"
        
if __name__ == '__main__':
    # Run Flask
    app.debug = True
    app.run()
