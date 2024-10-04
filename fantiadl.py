#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download media and other data from Fantia"""

import argparse
import getpass
import json
import time
import re
import netrc
import sys
import traceback
import datetime

import models

debug = False

__author__ = "bitbybyte"
__copyright__ = "Copyright 2023 bitbybyte"

__license__ = "MIT"
__version__ = "1.8.5"

BASE_HOST = "fantia.jp"
config_file = "settings.yml"
fanList = 'fanList.json'
complogfile = '/mnt/data/fantia_complate.json'

settings = {
    "session_id": "639032a2d82819cb330b640e0d5ebac09f3fe33338d97c56bf6944824f4fa6ab",
    "filename": "[post_id]_[file_id]",
    "output_dir": "/mnt/sns/fantia",
    "subdir_name": "[fanclub_name]（[creator_name]）/[posted_short]_[title]_[post_id]",
    "port": 8080
}
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
}

def write_settings(hint_disp):
    global settings
    settings["hint_disp"] = bool(hint_disp)
    try:
        with open(config_file, "w") as f:
            yaml.dump(settings, f)
    except:
        with open("log.txt", "w") as f:
            f.write("Settings save error.")

def writeFile(filename,msg,mode) :
    f = open(filename,mode)
    f.write(msg)
    f.close()

def readFile(filename) :
    f = open(filename, 'r')
    result_read_file = f.read()
    f.close()
    return result_read_file

def writeJson(filename,msg,mode) :
    with open(filename, mode) as f:
        json.dump(msg, f, ensure_ascii=False, indent=4)
 
def readJson(filename) :
    with open(filename,"r") as file:
        filedata=file.read()
    data = json.loads(filedata)
    return data 

if __name__ == "__main__":
    cmdl_usage = "%(prog)s [options] url"
    cmdl_version = __version__
    cmdl_parser = argparse.ArgumentParser(usage=cmdl_usage, conflict_handler="resolve")

    cmdl_parser.add_argument("-c", "--cookie", dest="session_arg", metavar="SESSION_COOKIE", help="_session_id cookie or cookies.txt")
    cmdl_parser.add_argument("-e", "--email", dest="email", metavar="EMAIL", help=argparse.SUPPRESS)
    cmdl_parser.add_argument("-p", "--password", dest="password", metavar="PASSWORD", help=argparse.SUPPRESS)
    cmdl_parser.add_argument("-n", "--netrc", action="store_true", dest="netrc", help=argparse.SUPPRESS)
    cmdl_parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="suppress output")
    cmdl_parser.add_argument("-v", "--version", action="version", version=cmdl_version)
    cmdl_parser.add_argument("url", action="store", nargs="*", help="fanclub or post URL")

    dl_group = cmdl_parser.add_argument_group("download options")
    dl_group.add_argument("-i", "--ignore-errors", action="store_true", dest="continue_on_error", help="continue on download errors")
    dl_group.add_argument("-l", "--limit", dest="limit", metavar="#", type=int, default=0, help="limit the number of posts to process per fanclub (excludes -n)")
    dl_group.add_argument("-o", "--output-directory", dest="output_path", help="directory to download to")
    dl_group.add_argument("-s", "--use-server-filenames", action="store_true", dest="use_server_filenames", help="download using server defined filenames")
    dl_group.add_argument("-r", "--mark-incomplete-posts", action="store_true", dest="mark_incomplete_posts", help="add .incomplete file to post directories that are incomplete")
    dl_group.add_argument("-m", "--dump-metadata", action="store_true", dest="dump_metadata", help="store metadata to file (including fanclub icon, header, and background)")
    dl_group.add_argument("-x", "--parse-for-external-links", action="store_true", dest="parse_for_external_links", help="parse posts for external links")
    dl_group.add_argument("-t", "--download-thumbnail", action="store_true", dest="download_thumb", help="download post thumbnails")
    dl_group.add_argument("-f", "--download-fanclubs", action="store_true", dest="download_fanclubs", help="download posts from all followed fanclubs")
    dl_group.add_argument("-p", "--download-paid-fanclubs", action="store_true", dest="download_paid_fanclubs", help="download posts from all fanclubs backed on a paid plan")
    dl_group.add_argument("-n", "--download-new-posts", dest="download_new_posts", metavar="#", type=int, help="download a specified number of new posts from your fanclub timeline")
    dl_group.add_argument("-d", "--download-month", dest="month_limit", metavar="%Y-%m", help="download posts only from a specific month, e.g. 2007-08 (excludes -n)")
    dl_group.add_argument("--exclude", dest="exclude_file", metavar="EXCLUDE_FILE", help="file containing a list of filenames to exclude from downloading")


    cmdl_opts = cmdl_parser.parse_args()

    session_arg = cmdl_opts.session_arg
    email = cmdl_opts.email
    password = cmdl_opts.password

    if (email or password or cmdl_opts.netrc) and not session_arg:
        sys.exit("Logging in from the command line is no longer supported. Please provide a session cookie using -c/--cookie. See the README for more information.")

    if not (cmdl_opts.download_fanclubs or cmdl_opts.download_paid_fanclubs or cmdl_opts.download_new_posts) and not cmdl_opts.url:
        sys.exit("Error: No valid input provided")

    if not session_arg:
        session_arg = input("Fantia session cookie (_session_id or cookies.txt path): ")


    try:
        if cmdl_opts.download_fanclubs:
            data = readJson(fanList)
            fanlist = data["fantiadata"]
            downloader = models.FantiaDownloader(session_arg=session_arg, dump_metadata=cmdl_opts.dump_metadata, parse_for_external_links=cmdl_opts.parse_for_external_links, download_thumb=cmdl_opts.download_thumb, directory=cmdl_opts.output_path, quiet=cmdl_opts.quiet, continue_on_error=cmdl_opts.continue_on_error, use_server_filenames=cmdl_opts.use_server_filenames, mark_incomplete_posts=cmdl_opts.mark_incomplete_posts, month_limit=cmdl_opts.month_limit, exclude_file=cmdl_opts.exclude_file)

            enddata = []
            jsonStr = {}
            jsonComp = {}

            compdata = []
            allcount = 0

            for i in fanlist :
                fanidtmp = i.split(":")
                fanid = fanidtmp[0]
                fanlast = fanidtmp[1]
                fanname = fanidtmp[2]
                endid = ""
                okid = fanlast
                count = 0
                print("fanid : %s / fanlast : %s / fanname : %s" % (str(fanid),str(fanlast),str(fanname)))  
                print("==================================================================================================")
                try:
                   posts = downloader.fetch_fanclub_posts_last(fanid, fanlast)
                   if len(posts) > 0:
                       for x in posts:
                          print("fanid %s : id %s" %(str(fanid),str(x)))
                          count+=1
                          downloader.download_post(x)
                          endid = x
                          okid = x
                except BaseException as e:
                   print("error :{}".format(e))
                   if debug == True:
                       print('Error {} happened, quit'.format(e))
                   endid = okid
                if (count == 0):
                    endid = fanlast
                endstr = str('%s:%s:%s' % (fanid,endid,fanname))
                enddata.append(endstr)

                onestr = str('%s:%s:%s' % (fanid,fanname,count))
                compdata.append(onestr)

                print("==================================================================================================")
                print("==================================================================================================")
                print("==================================================================================================")

                allcount += count

            jsonStr["fantiadata"] = enddata
            writeJson(fanList, jsonStr, 'w')

            #fantia_complate.jsonの書き込み処理
            now = datetime.datetime.now()
            dayTime = str("{0:04d}/{1:02d}/{2:02d} {3:02d}:{4:02d}".format(now.year,now.month,now.day,now.hour,now.minute))

            jsonStr = {}
            jsonStr["download-compleate"] = compdata
            jsonStr["dayTime"] = dayTime
            jsonStr["allcount"] = allcount
            writeJson(complogfile, jsonStr, 'w')

    except KeyboardInterrupt:
        sys.exit("Interrupted by user. Exiting...")
