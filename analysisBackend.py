from botocore.vendored import requests
import json

def returnLists(url):
    records = []
    nodes = []
    links = []
    receivedReply = []
    IDs = []
    created = []
    rows = []
    users = []
    dateCounter = {}
    
    payload = {'url':url} 
    r = requests.get('https://hypothes.is/api/search',params=payload)
    
    while len(records) < r.json()['total']: 
        records.extend(r.json()['rows']) 
        payload = {'url':url,'offset':len(records)} 
        r = requests.get('https://hypothes.is/api/search',params=payload) 
       
    for rt in records:
        IDs.append(rt['user'][5:-12])
        mon = str(int(rt['created'][5:7])-1)
        d = "("+rt['created'][:4]+", "+mon+", "+rt['created'][8:10]+")"
        created.append(d)
        if rt.get('references') is None:
            continue
        else:
            receivedReply.append(rt['references'][-1])
        
    userDict = {ni: indi for indi, ni in enumerate(set(IDs))}
 
    for c in created: 
        dateCounter[c] = created.count(c) 

    for p in dateCounter: 
        rows.append({"c":[{"v":"Date"+str(p)},{"v":dateCounter[p]}]})
    
    for r in records:
        users.append(r['user'][5:-12])
        if r.get('references') is not None:
            target = r['references'][-1]
            links.append({"source":r['id'],"target":target,"value":1})
            nodes.append({"id":r['id'],"user":r['user'][5:-12],"group":userDict[r['user'][5:-12]],"text":r['text'],"url":r['links']['incontext']})
        elif r['id'] in receivedReply:
            nodes.append({"id":r['id'],"user":r['user'][5:-12],"group":userDict[r['user'][5:-12]],"text":r['text'],"url":r['links']['incontext']})
    
    userList = list(set(users))
    return nodes,links,rows,userList
    
def lambda_handler(event, context):
    cols = [{"id":"Date","type":"date"},
            {"id":"Won/Loss","type":"number"}]
    testURL = event['path'][5:]
    n,l,r,u = returnLists(testURL)
    body = {
        "nodes":n,
        "links":l,
        "cols":cols,
        "rows":r,
        "users":u
    }
    return {
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body":json.dumps(body)
    }
