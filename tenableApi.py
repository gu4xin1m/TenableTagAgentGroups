import requests
import urllib.parse
import time
import logging
import os
from dotenv import load_dotenv


load_dotenv(override=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


TENABLE_ACCESS_KEY = os.getenv('TENABLE_ACCESS_KEY')
TENABLE_SECRET_KEY = os.getenv('TENABLE_SECRET_KEY')

if not TENABLE_ACCESS_KEY and not TENABLE_SECRET_KEY:
    print("Error: Could not load API keys from environment variables")
    exit()




headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-ApiKeys":f"accessKey={TENABLE_ACCESS_KEY};secretKey={TENABLE_SECRET_KEY}"
}

timeToWait = 5
baseURL = 'https://cloud.tenable.com'

def assetExport():

    endpoint = "/assets/export"
    url = baseURL+endpoint
    payload = {
        "filters": {"sources": ["NESSUS_AGENT"]},
        "chunk_size": 10000
    }
    response = requests.post(url, json=payload, headers=headers)
    export_uuid = response.json()
    return export_uuid['export_uuid']

# Sample output
# {
#   "export_uuid": "cfa4dc50-0f9d-41bb-b677-8f8da94bc1ed"
# }


def status(export_uuid):

    endpoint = "/assets/export/{}/status".format(export_uuid)
    url = baseURL+endpoint
    response = requests.get(url, headers=headers)
    return response.json()


# Sample output
#     {
#   "status": "FINISHED",
#   "chunks_available": [
#     1
#   ]
# }

def getAssets(export_uuid,chunk_id):
    export = status(export_uuid)
    print("[*]Geting tenable asset data...")
    while export['status'] != 'FINISHED':
        print("Waiting {} seconds for Tenable to generate the report".format(timeToWait))
        time.sleep(timeToWait)
        export = status(export_uuid)

    print("Done")
    print('[*] Downloading the report...')
    endpoint = '/assets/export/{}/chunks/{}'.format(export_uuid,chunk_id)
    url = baseURL+endpoint
    response = requests.get(url, headers=headers)
    return response.json()


def listAgentGroups():
    endpoint = '/scanners/104296/agent-groups'
    url = baseURL+endpoint
    response = requests.get(url, headers=headers)
    groups = response.json()
    groupsIdList = []
    for group in groups['groups']:
        groupsIdList.append(group['id'])
    
    return groupsIdList


def getAgentGroupDetail(agentGroupId):
    endpoint = '/scanners/104296/agent-groups/'+str(agentGroupId)+'?limit=5000'
    url = baseURL+endpoint
    response = requests.get(url, headers=headers)
    return response.json()


def getTagId(AgentgroupName):
    endpoint = "/tags/values?f=value%3Amatch%3A"+urllib.parse.quote(AgentgroupName)
    url = baseURL+endpoint
    response = requests.get(url, headers=headers)
    responseList = {}
    try:
        responseJson = response.json()
        responseList['uuid'] = responseJson["values"][0]['uuid']
        responseList['category_name'] = responseJson["values"][0]['category_name']
        responseList['value'] = responseJson["values"][0]['value']
        return responseList
    except:
        print(f"Could not find a matching tag category for agent group: {AgentgroupName}")

def getTargetAssets(agentGroupId,assets):
    agentGroup = getAgentGroupDetail(agentGroupId)
    assets_idlist = []
    for line in agentGroup['agents']:
        agentName = line['name']
        for asset in assets:
         if agentName in asset['agent_names']:
            assets_idlist.append(asset['id'])
    
    return assets_idlist


def tagAssets(tagUuid:str,assets:list):
    payload = {
    "assets": assets,
    "tags": [tagUuid],
    "action": "add"
    }
    endpoint = '/tags/assets/assignments'
    url = baseURL+endpoint
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
