import flask
from flask import Flask, jsonify, request, make_response 

import json

import requests
from requests.models import Response

app = Flask(__name__)

#Exception for missing parameter in URL
class InvalidSyntax(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidSyntax)
def handle_invalid_syntax(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#Exception for BitBucket repo not found
class InvalidBitBucketOrg(Exception):
    status_code = 404

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidBitBucketOrg)
def handle_invalid_bitbucket_org(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#Exception for GitHub repo not found
class InvalidGitHubOrg(Exception):
    status_code = 404

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidGitHubOrg)
def handle_invalid_github_org(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#Exception for invalid entry on either platform
class InvalidAll(Exception):
    status_code = 404

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidAll)
def handle_invalid_all(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/v1/bitbucket', methods=['GET'])
def get_bitbucket():
    """ Endpoint for BitBucket information only. Basic organization/team data provided as response. Exceptions will be thrown for both incorrectly formatted URL
    as well as organization not found on BitBucket platform """
    if 'org' in request.args:
        org = request.args['org']
        response = requests.get('https://api.bitbucket.org/2.0/teams/%s'% org)
        data = response.json()
        if 'error' in data:
            raise InvalidBitBucketOrg('Organization does not exist on BitBucket platform. Please try again', status_code = 404)
        else:
            return jsonify(data)
    else:
        raise InvalidSyntax('Organization not entered. Invalid request', status_code=400)

@app.route('/v1/github', methods=['GET'])
def get_github():
    """ Endpoint for GitHub information only. Basic organization/team data provided as response. Exceptions will be thrown for both incorrectly formatted URL
    as well as organization not found on GitHub platform.""" 
    if 'org' in request.args:
        org = request.args['org']
        response = requests.get('https://api.github.com/orgs/%s'% org)
        data = response.json()
        if 'message' in data:
            raise InvalidGitHubOrg('Organization does not exist on GitHub platform. Please try again', status_code = 404)
        else:
            return jsonify(data)
    else:
        raise InvalidSyntax('Organization not entered. Invalid request', status_code=400)
 
@app.route('/v1/comboorgs', methods=['GET'])
def get_orgs():
    """ Endpoint for aggregating of data across both platforms.  Exceptions to be thrown for incorrect URL syntax as well as 
    organization not found on either or both platforms. Assumes that organization names are the same on GitHub and BitBucket.  In the event that
    this proves to be a miscalculation, a second URL parameter could be added """
    if 'org' in request.args:
        org = request.args['org']
        gh_response = requests.get('https://api.github.com/orgs/%s' % org)
        gh_json_rsp = gh_response.json()
        bb_response = requests.get('https://api.bitbucket.org/2.0/repositories/%s'% org)
        bb_json_rsp = bb_response.json()
        #verify that request is valid and processing can continue
        if ('message' in gh_json_rsp) and ('error' in bb_json_rsp):
            raise InvalidAll('Organization does not exist on either platform. Please try again', status_code = 404)
        elif 'message' in gh_json_rsp:
            raise InvalidGitHubOrg('Organization does not exist on GitHub platform. Please try again or use ../v1/bitbucket endpoint', status_code = 404)
        elif 'error' in bb_json_rsp:
            raise InvalidBitBucketOrg('Organization does not exist on BitBucket platform. Please try again or use ../v1/github endpoint', status_code = 404)

        #bitbucket data points
        bb_public_repo = bb_json_rsp['size']
        bb_total_forked = 0
        bb_total_watchers = 0
        bb_languages = []
        bb_descriptions = []
        for b in bb_json_rsp['values']:
            #get url for forks of each repo
            forks_link = str(b['links']['forks']['href'])
            #call api for forks
            bb_forked_response = requests.get('%s' % forks_link)
            bb_forked_json = bb_forked_response.json()
            #find number of forks per repo
            bb_forked_size = bb_forked_json['size']
            #add to total
            bb_total_forked = bb_total_forked + bb_forked_size
            #get url for watchers of each repo
            watchers_link = str(b['links']['watchers']['href'])
            #call api for watchers
            bb_watchers_response = requests.get('%s' % watchers_link)
            bb_watchers_json = bb_watchers_response.json()
            #find number of watchers per repo
            bb_watchers_size = bb_watchers_json['size']
            #add to total
            bb_total_watchers = bb_total_watchers + bb_watchers_size
            #create list of unique listings of languages used
            if b['language'] not in bb_languages:
                bb_languages.append(b['language'])
            #create list of unique descriptions of repos
            if b['description'] not in bb_descriptions:
                bb_descriptions.append(b['description'])
        bb_descriptions_total = len(bb_descriptions)

        #github data points
        gh_public_repo = gh_json_rsp['public_repos']
        #drill down to repos
        gh_repos_response = requests.get('https://api.github.com/orgs/%s/repos' % org)
        gh_repos_json = gh_repos_response.json()
        gh_total_forked = 0
        gh_total_watchers = 0
        gh_descriptions = []
        gh_languages = []
        for g in gh_repos_json:
            #total up forks per repo
            gh_total_forked = gh_total_forked + g['forks'] 
            #total watchers per repo
            gh_total_watchers = gh_total_watchers + g['watchers']
            #create list of unique descriptions of repos
            if g['description'] not in gh_descriptions:
                gh_descriptions.append(g['description'])    
            #get languages used for a repo
            gh_languages_link = str(g['languages_url'])
            gh_languages_response = requests.get('%s' % gh_languages_link)
            gh_languages_json = gh_languages_response.json()
            #create list of unique languages used
            for g in gh_languages_json:
                if g not in gh_languages:
                    gh_languages.append(g)
        gh_descriptions_total = len(gh_descriptions)

        #totals
        public_repos_total = gh_public_repo + bb_public_repo
        forked_total = bb_total_forked + gh_total_forked
        watchers_total = bb_total_watchers + gh_total_watchers
        languages_combined = bb_languages + gh_languages
        deduped_languages_combined = list(set(map(str.capitalize, languages_combined))) 
        languages_total = len(deduped_languages_combined)
        descriptions_combined = bb_descriptions + gh_descriptions
        descriptions_total = bb_descriptions_total + gh_descriptions_total
         
        return jsonify({'org name':org, 'public repos':public_repos_total, 'forked repos':forked_total, 'watchers':watchers_total, 'languages used': deduped_languages_combined, 'number of unique languages': languages_total, 'repo descriptions and topics': descriptions_combined, 'number of unique descriptions': descriptions_total}) 
    else:
        raise InvalidSyntax('Organization not entered. Invalid request', status_code=400)

