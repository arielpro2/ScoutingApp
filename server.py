import secrets
import sys
import javaobj
import csv
import flask
import os
import base64
import logging


from flask import jsonify, render_template, request, session, redirect
from flask_session import Session


app = flask.Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config["DEBUG"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def retSecretFromAdminToken(token):
    with open("secrets",'r') as secrets:
        for row in secrets:
            n = row.strip().split(":")
            if len(n) != 3:
                continue
            if n[2] == token:
                return n[1:2]
    return None


@app.route('/')
@app.route('/index')
def Index():
    return render_template("index.html")

@app.route('/PrivacyPolicy')
def PrivacyPolicy():
    return render_template("privacyPolicy.html")

@app.route('/register', methods=['POST','GET'])
def Register():
    if request.method == "POST":
        if session.get("admin-token"):
            return render_template("alreadyRegistered.html",adminToken=session.get("admin-token"), memberToken = session.get("member-token"))

        memberToken = secrets.token_urlsafe(16)
        adminToken = secrets.token_urlsafe(16)
        with open("secrets",'a') as secretfile:
            secretfile.write(f"\n{request.form.get('TeamNumber')}:{memberToken}:{adminToken}")

        os.chdir(r'TeamData')

        with open(f"{memberToken}.csv",'w') as file:
            file.write("Alias,TeamNumber,GameNumber,b_defence,b_unsure,b_offence,AutoUpper,AutoLower,TeleUpper,TeleLower,Ranking,Notes,C1,C2,C3,C4")

        os.chdir('..')

        session["admin-token"] = adminToken
        session["member-token"] = memberToken
        return render_template("successMessage.html",memberToken=memberToken, adminToken=adminToken)

    return render_template("index.html")
@app.route('/api/login')
def Login():
    with open("secrets",'r') as secretfile:
        for line in secretfile:
            line = line.strip().split(':')
            if len(line) == 3:
                if line[1] == request.args.get('token'):
                        return "True"
            else:
                continue
        return "False"

@app.route('/api/admin')
def Admin():
    if (retSecretFromAdminToken(request.args.get('token'))):
        return "True"
    return "False"


@app.route('/api/createEntry', methods=['GET'])
def createEntry():
    entryString = base64.b64decode(request.args.get('object')).decode('utf-8').replace(":", ",")
    os.chdir(r'TeamData')
    if not os.path.isfile(f"{request.args.get('token')}.csv"):
        return "Error: <br> Bad key!"
    with open(f"{request.args.get('token')}.csv", "r+") as table:
        os.chdir('..')
        csvTable = csv.DictReader(table)
        entryList = entryString.split(',')
        if not [True for row in csvTable if row['TeamNumber'] == entryList[1] and row['GameNumber'] == entryList[2]]:
            table.write("\n"+entryString)
            table.close()
        else:
            return "Error! Entry for team and game number specified was already created!"
    return "successfully created entry"

@app.route('/api/filterEntries', methods=['GET'])
def filterEntries():
    if adminToken := request.args.get("token"):
        if (memberToken := retSecretFromAdminToken(adminToken)):
            os.chdir(r'TeamData')
            with open(f"{memberToken[0]}.csv", 'r') as table:
                os.chdir(r'..')
                return '\n'.join(table.readlines()[request.args.get("line"):])
    return "Please provide an admin token to get entries"

@app.route('/api/editEntry')
def editEntry():
    if adminToken := request.args.get("token"):
        if(memberToken := retSecretFromAdminToken(adminToken)):
            os.chdir(r'TeamData')
            with open (f'{memberToken[0]}.csv', 'r+') as table:
                os.chdir(r'..')
                new = base64.b64decode(request.args.get("new")).decode()
                old = base64.b64decode(request.args.get("old")).decode()
                oldfile = table.readlines()
                lines = [new if old in row else row.rstrip() for row in oldfile]
                table.seek(0)
                table.truncate(0)
                table.write('\n'.join(lines))
                newfile = table.readlines()
                if oldfile == newfile:
                    return "Line not found"
            return "Success"
    return "Please provide an admin token to edit entry"

        


app.run(host="0.0.0.0",port=80)