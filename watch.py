#!/usr/bin/env python

import os
from kubernetes import client, config, watch
import ssl
import urllib2
import urllib
import subprocess, shlex
import time 
def main():
    api_key = "LUFRPT16Y1BlcXJWSUZrZ3IyQ1BiMXN2d3hSSDhLcUE9eXJiT0ZUdzkyU3I1ZjNIWDhaYzVCTmJaZGhHeFljUWZYQXlQMGViQ1Z6Yz0="
    FWXMLUpdate = []
    XMLHeader = "<uid-message><version>1.0</version><type>update</type><payload>"
    XMLFooter = "</payload></uid-message>"
    Register = "<register>"
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ip = subprocess.check_output(shlex.split("gcloud --format='value(networkInterfaces[0].accessConfigs[0].natIP)' compute instances list --filter='name=firewall1'")).rstrip()
    config.load_kube_config(os.path.join(os.environ["HOME"], '.kube/config'))
    v1 = client.CoreV1Api()
    mysvc = watch.Watch().stream(v1.list_pod_for_all_namespaces)
    for event in mysvc:
        Register += '<entry ip="' + event['object'].status.pod_ip + '">'
        Register += "<tag>"
        for i in event['object'].metadata.labels:
            Register += "<member>" + event['object'].metadata.labels[i] + "</member>"
        Register += "</tag>"
        Register += "</entry>"
        Register += '</register>'
        FWXMLUpdate = XMLHeader + Register + XMLFooter
        url = "https://%s/api/?type=user-id&action=set&key=%s&cmd=%s" % (ip, api_key,urllib.quote(FWXMLUpdate))
        time.sleep(0.5)
        try:
            response = urllib2.urlopen(url,context=gcontext).read()
        except urllib2.HTTPError, e:
           print "HTTPError = " + str(e)
            
if __name__ == '__main__':
    main()
