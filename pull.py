#!/usr/bin/python
# -*- coding: utf-8 -*-
# v1.3
import sys
import subprocess
import os
import time
import argparse
import json
import re
# from pprint import pprint
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
 
 
# you can edit
git_usr_name = 'READ_ONLY'
git_password = 'ahputh3shi'
log_dir = '/var/log/'
log_file_name = os.path.basename(__file__) + '.log' #will be real_py_file_name .log
default_www_dir = "/var/www/"
default_port = 8000
default_chattr = 'n'
git_default_branch = 'master'
git_default_repository = '*requared*'
git_default_clean = 'n'
git_config_dir = '.git'
 
class Webhook(BaseHTTPRequestHandler):
 
    def do_POST(self):
        message = 'OK'
        self.rfile._sock.settimeout(5)
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.send_header("Content-type", "text")
        self.send_header("Content-length", str(len(message)))
        self.end_headers()
        self.wfile.write(message)
 
        # parse data
        data = json.loads(data_string)
 
        # Process here sent data
        # pprint(data)
 
        if args.www_dir != default_www_dir:
            pull_www_dir = args.www_dir
            rm_rule1 = '*'
            rm_rule2 = '.*'
        else:
            pull_www_dir = default_www_dir + data['repository']['name']
            rm_rule1 = '/*'
            rm_rule2 = '/.*'
 
        git_url = data['repository']['git_http_url'].replace("://",("://" + git_usr_name + ":" + git_password + "@"))
        git_branch_name = re.match('refs/heads/([0-9a-zA-Z_]+)$', data['ref']).group(1)
 
        # print git_url
        # print git_branch_name
        # print pull_www_dir
 
        if (data['repository']['name'] == args.repository) and (git_branch_name == args.branch):
            if args.chattr != default_chattr:
                subprocess.call([("chattr -i -R " + pull_www_dir)], shell=True)
 
            if os.path.isdir(pull_www_dir):
                os.chdir(pull_www_dir)
                if os.path.isdir(git_config_dir):
                    subprocess.call(["git reset --hard HEAD"], shell=True)
                    if args.clean != git_default_clean:
                        subprocess.call(["git clean -f -d"], shell=True)
                    git_res = subprocess.call([("git pull " + git_url + " " + git_branch_name)], shell=True)
                    os.chdir(log_dir)
                    log_file = open(log_file_name, "a")
                    if git_res == 0:
                        log_file.write("PORT: " + str(args.port) + " PULL-DONE " + data['checkout_sha'] + " " + data['user_email'] + " " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
                    else:
                        log_file.write("PORT: " + str(args.port) + " PULL-ERROR " + data['checkout_sha'] + " " + data['user_email'] + " " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
                    log_file.close()
                else:
                    if args.clean != git_default_clean:
                        subprocess.call(["rm -rf " + pull_www_dir + rm_rule1 + ""], shell=True)
                        subprocess.call(["rm -rf " + pull_www_dir + rm_rule2 + ""], shell=True)
                        git_res = subprocess.call([("git clone -b " + git_branch_name + " " + git_url + " " + pull_www_dir)], shell=True)
                        os.chdir(log_dir)
                        log_file = open(log_file_name, "a")
                        if git_res == 0:
                            log_file.write("PORT: " + str(args.port) + " CLONE-DONE (NO .git | CLEAN YES) " + data['checkout_sha'] + " " + data['user_email'] + " " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
                        else:
                            log_file.write("PORT: " + str(args.port) + " CLONE-ERROR (NO .git | CLEAN YES) " + data['checkout_sha'] + " " + data['user_email'] + " " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
                        log_file.close()
                    else:
                        os.chdir(log_dir)
                        log_file = open(log_file_name, "a")
                        log_file.write("PORT: " + str(args.port) + " CLONE-ERROR (NO .git | CLEAN NO) " + data['checkout_sha'] + " " + data['user_email'] + " " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
                        log_file.close()
            else:
                git_res = subprocess.call([("git clone -b " + git_branch_name + " " + git_url + " " + pull_www_dir)], shell=True)
                os.chdir(log_dir)
                log_file = open(log_file_name, "a")
                if git_res == 0:
                    log_file.write("PORT: " + str(args.port) + " CLONE-DONE " + data['checkout_sha'] + " " + data['user_email'] + " " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
                else:
                    log_file.write("PORT: " + str(args.port) + " CLONE-ERROR " + data['checkout_sha'] + " " + data['user_email'] + " " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
                log_file.close()
               
            if args.chattr != default_chattr:
                subprocess.call([("chattr +i -R " + pull_www_dir)], shell=True)
               
if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='{} description'.format(os.path.basename(__file__)))
 
    # Prepare settings
    parser.add_argument('-p', '--port', help='Server port ({} will be used by default)'.format(default_port), default=default_port, type=int)
    parser.add_argument('-w', '--www-dir', help='Server pull www dir ({} will be used by default) !!! / in end !!!'.format(default_www_dir), default=default_www_dir)
    parser.add_argument('-r', '--repository', help='Listen to repository action ({} will be used by default)'.format(git_default_repository), default=git_default_repository)
    parser.add_argument('-b', '--branch', help='Listen to branch action ({} will be used by default)'.format(git_default_branch), default=git_default_branch)
    parser.add_argument('-c', '--clean', help='Git git clean -f -d (y or n) ({} will be used by default)'.format(git_default_clean), default=git_default_clean)
    parser.add_argument('-t', '--chattr', help='Remove chattr (y or n) ({} will be used by default)'.format(default_chattr), default=default_chattr)
 
    args = parser.parse_args()
 
    # if args.log:
 
    # Launch server
    try:
        server = HTTPServer(('', args.port), Webhook)
        os.chdir(log_dir)
        log_file = open(log_file_name, "a")
        log_file.write("START PORT: " + str(args.port) + " MAIN_WWW_DIR: " + args.www_dir + " REPOSITORY: " + args.repository + " BRANCH: " + args.branch + " CLEAN: " +  args.clean + " CHATTR: " + args.chattr + " TIME: " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
        log_file.close()
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
    except Exception, e:
        os.chdir(log_dir)
        log_file = open(log_file_name, "a")
        log_file.write("ERROR M.B. " + str(e) + " " + time.strftime("%m-%d-%Y %H:%M:%S") + "\n")
        log_file.close()
        print str(e)



