import tenableApi

exportID = tenableApi.assetExport()
assets = tenableApi.getAssets(exportID,1)
agent_groups =  tenableApi.listAgentGroups()


for agentGroup in agent_groups:

    #Get all information about the AG
    agentGroupDetails = tenableApi.getAgentGroupDetail(agentGroup)
    
    # Get assets ids based on agent group
    targets = tenableApi.getTargetAssets(agentGroup,assets)
    
    if targets:
        agentGroupName = agentGroupDetails['name']
        #Identify the tag name based on the Asset group Name
        tag = tenableApi.getTagId(agentGroupName)
        
        #Tag assets
        print('[*] Applying tags for agent group: {}, Agents: {}'.format(agentGroupName,len(targets)))
        tenableApi.tagAssets(tag,targets)


