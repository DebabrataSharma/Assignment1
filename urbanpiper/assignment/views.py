from django.shortcuts import render
from django.http import HttpResponse
import json
import http.client
import os.path
from os import path
from aylienapiclient import textapi
from django.contrib import messages
from django.http import HttpResponseRedirect


# Create your views here.

def home(request):
    client = textapi.Client("68c8ca14", "34fcfcadedc02e9f2c2bc407696720e9") #connect to aylien api for sentiment analysis
    conn = http.client.HTTPSConnection("hacker-news.firebaseio.com")
    payload = "{}"
    conn.request("GET", "/v0/topstories.json?print=pretty", payload)
    res = conn.getresponse()
    data = res.read()
    json_data = getStoryId(data) #X

    if path.exists("data.json") is False:
        json_file_data = checkFile(json_data[0:100], conn, client, payload, [])
        store(json_file_data)
        return render(request,'home.html', {'list':json_file_data})


    else:
        json_file_data = copyFile()
        json_file_data = checkFile(json_data[0:100],conn,client, payload, json_file_data)
        return render(request,'home.html', {'list' : json_file_data})

def getStoryId(data):
    return (json.loads(data.decode("utf-8")))


def checkFile(json_data, conn, client,payload,json_file_data=[]):
        if bool(json_file_data) == False: # file is not created yet
            for i in range(0,len(json_data)):
                request1 = "/v0/item/" + str(json_data[i]) + ".json?print=pretty"
                conn.request("GET",request1, payload)
                res1 = conn.getresponse()
                data1 = res1.read()
                content = json.loads(data1.decode('utf-8')) #Y
            #    senti = addSentiment(content,client)
                json_file_data.append(content)
            return(json_file_data)
            
           
        
        else:
            temp_json_file = []
            for i in json_data:
                for j in json_file_data:
                    if  i==j['id']:
                        temp_json_file.append(j)
                        break
                    
                    if j ==json_file_data[len(json_file_data)-1] and i!=j:#new trending article
                        request1 = "/v0/item/" + str(i) + ".json?print=pretty"
                        conn.request("GET",request1, payload)
                        res1 = conn.getresponse()
                        data1 = res1.read()
                        j_f_d = json.loads(data1.decode('utf-8'))
                        #senti = addSentiment(j_f_d,client)
                        temp_json_file.append(j_f_d)
                        json_file_data.append(j_f_d) #Y            
            store(json_file_data)
            return(json_file_data)                                        


def addSentiment(data,client):
        sentiment = client.Sentiment({'text': data['title']})
        data['polarity'] = sentiment['polarity']
        data['polarity_confidence'] = sentiment['polarity_confidence']
        data['subjectivity_confidence'] = sentiment['subjectivity_confidence']
        return(data)


def store(json_file_data):
    with open ("data.json","w+") as output:
        json.dump(json_file_data,output)
    

def copyFile():
    with open('data.json','r') as output:
        file_json_obj = json.load(output)#Z
    return(file_json_obj)

def search(request):
    if request.method=='POST':
        srch = request.POST['srh']
        json_file_data = copyFile()
        if srch:
            for i in range(0,len(json_file_data)):
                if str(srch)==json_file_data[i]['title']:
                    return render(request,'search_result.html',json_file_data[i])
            return render(request,'search_result.html',{'srch':'not'})
        else:
            return HttpResponseRedirect('http://127.0.0.1:8000/')
        
    
