#! /usr/bin/env python3
#-*- coding:utf-8 -*-

'''
'''

import argparse
import json
import urllib.parse as uparse
import socketserver
from http.server import SimpleHTTPRequestHandler

class DebugHandler(SimpleHTTPRequestHandler):
    '''
    '''
    def parser(self, response):
        '''
        '''
        purl=uparse.urlparse(self.path)
        response['path']=purl.path
        response['url_params']=dict(uparse.parse_qsl(purl.query))
        response['headers']={k:v for k,v in self.headers.items()}
        response['method']=self.command
        response['client_address']={'host':self.client_address[0], 'port':self.client_address[1]}
        if 'format' not in response['url_params']:
            response_json=json.dumps(response) 
        else:
            uparams=response['url_params']['format']
            if uparams == 'pretty_json':
                response_json=''.join(['<pre>', 
                                    json.dumps(response, 
                                                indent=3, 
                                                sort_keys=True), 
                                    '</pre>'])
            elif uparams =='json':
                response_json=json.dumps(response) 
            else:
                response_json=json.dumps({'error':'Unkown format'})
        return response_json

    def do_GET(self):
        '''
        '''
        response={}
        response_json=self.parser(response)
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        self.wfile.write(response_json.encode())
        
        return
    
    def do_POST(self):
        '''
        '''
        response={}
        length=int((self.headers['Content-Length'])) #prevent non stop reading
        response['data']=dict(uparse.parse_qsl(self.rfile.read(length).decode()))
        response_json=self.parser(response)
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        self.wfile.write(response_json.encode())
        
        return

#########################################################
if __name__ == '__main__':
    
    parser=argparse.ArgumentParser(description='Very simple debug server')
    parser.add_argument('-P', '--port', default=8000)
    parser.add_argument('-H', '--host', default='127.0.0.1')
    args = parser.parse_args()

    
    httpd = socketserver.TCPServer((args.host, args.port), DebugHandler)

    print("[+] DEBUG SERVER ON")
    print("[+] MAKE REQUESTS TO {}:{}".format(args.host, args.port))
    httpd.serve_forever()




