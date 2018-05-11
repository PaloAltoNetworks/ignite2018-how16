#!/usr/bin/env python

import os
from kubernetes import client, config, watch
import ssl
import urllib2
import urllib
import subprocess, shlex
import time 
import threading
import time
import site
import sys
import itertools

gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
ip = subprocess.check_output(shlex.split("gcloud --format='value(networkInterfaces[0].accessConfigs[0].natIP)' compute instances list --filter='name=firewall1'")).rstrip()
api_key = "LUFRPT16Y1BlcXJWSUZrZ3IyQ1BiMXN2d3hSSDhLcUE9eXJiT0ZUdzkyU3I1ZjNIWDhaYzVCTmJaZGhHeFljUWZYQXlQMGViQ1Z6Yz0="
config.load_kube_config(os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()
v2 = client.CoreV1Api()
v3 = client.CoreV1Api()



def services():
    mysvcs = watch.Watch().stream(v2.list_service_for_all_namespaces)
    for event1 in mysvcs:
        if event1['type'] == 'MODIFIED' and event1['object'].metadata.namespace == 'default':
            FWXMLUpdate = []
            XMLHeader = "<uid-message><version>1.0</version><type>update</type><payload>"
            XMLFooter = "</payload></uid-message>"
            Register = "<register>"        
            if event1['object'].spec.type == "LoadBalancer":
                Register += '<entry ip="' + event1['object'].status.load_balancer.ingress[0].ip + '">'
            else:
                Register += '<entry ip="' + event1['object'].spec.cluster_ip + '">'
            Register += "<tag>"                
            Register += "<member>" + event1['object'].metadata.name + "-svc" + "</member>"
            Register += "</tag>"
            Register += "</entry>"
            Register += '</register>'
            FWXMLUpdate = XMLHeader + Register + XMLFooter
            url = "https://%s/api/?type=user-id&action=set&key=%s&cmd=%s" % (ip, api_key,urllib.quote(FWXMLUpdate))
            try:
                response = urllib2.urlopen(url,context=gcontext).read()
            except urllib2.HTTPError, e:
                print "HTTPError = " + str(e)


def pods():
    mypods = watch.Watch().stream(v1.list_pod_for_all_namespaces)
    for event in mypods:
        if event['type'] == 'MODIFIED' and event['object'].metadata.namespace == 'default' and event['object'].status.pod_ip is not None:
            FWXMLUpdate = []
            XMLHeader = "<uid-message><version>1.0</version><type>update</type><payload>"
            XMLFooter = "</payload></uid-message>"
            Register = "<register>"        
            Register += '<entry ip="' + event['object'].status.pod_ip + '">'
            Register += "<tag>"
            for i,j in event['object'].metadata.labels.iteritems():
                Register += "<member>" + j + "-" + i + "-pod" + "</member>"
            Register += "</tag>"
            Register += "</entry>"
            Register += '</register>'
            FWXMLUpdate = XMLHeader + Register + XMLFooter
            url = "https://%s/api/?type=user-id&action=set&key=%s&cmd=%s" % (ip, api_key,urllib.quote(FWXMLUpdate))
            try:
                response = urllib2.urlopen(url,context=gcontext).read()
            except urllib2.HTTPError, e:
                print "HTTPError = " + str(e)
        else:
            continue




def nodes():
    mynodes = v3.list_node()
    for i in mynodes.items:
        for j in i.status.addresses:
            if j.type == "InternalIP":
                nodeip = j.address
            elif j.type == "Hostname":
                name = j.address

        FWXMLUpdate = []
        XMLHeader = "<uid-message><version>1.0</version><type>update</type><payload>"
        XMLFooter = "</payload></uid-message>"
        Register = "<register>" 

        Register += '<entry ip="' + nodeip + '">'
        Register += "<tag>"
        Register += "<member>" + name + "</member>"
        Register += "</tag>"
        Register += "</entry>"
        Register += '</register>'
        FWXMLUpdate = XMLHeader + Register + XMLFooter
        url = "https://%s/api/?type=user-id&action=set&key=%s&cmd=%s" % (ip, api_key,urllib.quote(FWXMLUpdate))
        try:
            response = urllib2.urlopen(url,context=gcontext).read()
        except urllib2.HTTPError, e:
            print "HTTPError = " + str(e)


def main():
    t1 =  threading.Thread(name='watch_pods',target=pods, args=())
    t1.daemon = True
    t1.start()
    t2 =  threading.Thread(name='watch_svcs',target=services, args=())
    t2.daemon = True
    t2.start()
    t3 =  threading.Thread(name='watch_nodes',target=nodes, args=())
    t3.daemon = True
    t3.start()    
    while threading.active_count() > 0:
        time.sleep(1)


if __name__ == '__main__':
    main()