import javaobj
import flask
import json
from flask import request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/api/createEntry', methods=['GET'])
def createEntry():
    objectbytes = request.args.get('object')
    pobj = javaobj.loads(bytearray.fromhex(objectbytes))
    with open("entries.json") as fp:
        entries = json.load(fp)
    entries.append({
        "TeamNumber":pobj.TeamNumber,
        "GameNumber":pobj.GameNumber,
        "b_defence":pobj.b_defence,
        "b_unsure":pobj.b_unsure,
        "b_offence":pobj.b_offence,
        "AutoUpper":pobj.AutoUpper,
        "AutoLower":pobj.AutoLower,
        "TeleUpper":pobj.TeleUpper,
        "TeleLower":pobj.TeleUpper,
        "Ranking":pobj.Ranking,
        "Notes":pobj.Notes,
        "Climbing1":pobj.Climbing[0],
        "Climbing2":pobj.Climbing[1],
        "Climbing3":pobj.Climbing[2],
        "Climbing4":pobj.Climbing[3],
    })
    with open("entries.json", 'w') as json_file:
        json.dump(entries, json_file, indent=4,separators=(',',': '))
    return "succsesfully created entry"
    
@app.route('/api/print', methods=['GET'])
def print():
    objectbytes = request.args.get('object')
    pobj = javaobj.loads(bytearray.fromhex(objectbytes))
    return str(dir(pobj))

app.run()

