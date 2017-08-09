#!/usr/bin/python3
############################
# Adding domains to zabbix #
############################
import os, json, os, sys, urllib3, requests
import xml.etree.ElementTree as ET

# Defining variables for authorization on 'namecheap' API
ncUser = sys.argv[1]
apiUser = sys.argv[2]
apiKey = sys.argv[3]
clientIp = sys.argv[4]
domain = ''
apiToken = {'result': 'None'}

# JSON Data
jsonAuth = {
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "user": "",
        "password": ""
    },
    "id": 1,
    "auth": None
}

# Itiniating GET request to obtain token
initManager = urllib3.PoolManager()
jsonUrl = 'http://url/to/zabbix/host/api_jsonrpc.php'
getRequest = initManager.request('GET', jsonUrl, body = json.dumps(jsonAuth), headers = {'Content-Type': 'application/json'})
apiToken = json.loads(getRequest.data.decode('utf-8'))
print(apiToken['result'])


# Command used to get info from 'namecheap' provider
apiCommand = 'curl -s "https://api.namecheap.com/xml.response?ApiUser='+ apiUser +'&ApiKey=' + apiKey + '&UserName=' + ncUser + '&ClientIp=' + clientIp + '&Command=namecheap.domains.getList&PageSize=100&Page=1" > domains.xml'
os.system(apiCommand)

# Parsing 'domain'.xml data
fileTree = ET.parse('domains.xml')
root = fileTree.getroot()
for child in root.findall('.//{http://api.namecheap.com/xml.response}Domain'):
    print(apiToken['result'])
    domain = child.get('Name')

    # JSON data for adding a new domain
    jsonPost = {
        "jsonrpc": "2.0",
        "method": "host.create",
        "params": {
            "host": domain,
            "interfaces": [
                {
                    "type": 1,
                    "main": 1,
                    "useip": 1,
                    "ip": "127.0.0.1",
                    "dns": "",
                    "port": "10050"
                }
            ],
            "groups": [
                {
                    "groupid": "17"
                }
            ],
            "templetes": [
                {
                    "templateid": "10239"
                }
            ],
            "macros": [
                {
                    "macro": "{$APIKEY}",
                    "value": apiKey
                },
                {
                    "macro": "{$APIUSER}",
                    "value": apiUser
                },
                {
                    "macro": "{$CLIENTIP}",
                    "value": clientIp
                },
                {
                    "macro": "{$DOMAIN}",
                    "value": domain
                },
                {
                    "macro": "{$NCUSER}",
                    "value": ncUser
                }
            ]
        },
        "id": 1,
        "auth": apiToken['result']
    }
    postRequest = initManager.request('POST', jsonUrl, body = json.dumps(jsonPost), headers = {'Content-Type': 'application/json'})
    print(json.dumps(jsonPost))
    print(postRequest.status)
    print(postRequest.data.decode('utf-8'))
    print("=================================")

    # Resolving host ID
    jsonHostGet = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": "extend",
            "filter": {
                "host": domain
            },
        },
        "auth": apiToken['result'],
        "id": 1
    }
    getHostRequest = initManager.request('GET', jsonUrl, body = json.dumps(jsonHostGet), headers = {'Content-Type': 'application/json'})
    dataHost = json.loads(getHostRequest.data.decode('utf-8'))
    print(getHostRequest.data)
    print(dataHost['result'][0]['hostid'])

    # Updating template links to the host
    print("=================================")
    jsonMacroUpdate = {
        "jsonrpc": "2.0",
        "method": "template.massadd",
        "params": {
            "templates": [
                {
                    "templateid": "10239"
                }
            ],
            "hosts": [
                {
                    "hostid": dataHost['result'][0]['hostid']
                }
            ]
        },
        "auth": apiToken['result'],
        "id": 1
    }
    updateHostRequest = initManager.request('POST', jsonUrl, body = json.dumps(jsonMacroUpdate), headers = {'Content-Type': 'application/json'})
    print(updateHostRequest.status)
    print(updateHostRequest.data)
