#!/usr/bin/env python
# coding: utf-8

import requests
import json
from datetime import datetime
import time
import re
import os
import argparse

# Argument parser for command-line arguments
parser = argparse.ArgumentParser(description="Script to fetch data from Tavern Keeper API.")
parser.add_argument("--user_id", required=True, help="User ID for the API")
parser.add_argument("--session_id", required=True, help="Session ID for authentication")
args = parser.parse_args()

# Command-line arguments
user_id = args.user_id
session_id = args.session_id

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
export_dir = f"export_data_{timestamp}"
sleep_delay = 0.5


def get_tk_data(req, paged_type=None):
    host = r"https://www.tavern-keeper.com"
    url = host + req
    
    headers = {
        "Accept" : r"application/json",
        'Content-Type': 'application/json',
        "cookie" : f"tavern-keeper={session_id}",
        "X-CSRF-Token" : "something"
    }
    
    outdata = []  # List to hold paged data
    page = 1  # Start with the first page
    
    if paged_type:
        # print ('data type is paged')
        while True:
            paginated_url = f"{url}?page={page}"
            time.sleep(0.5)
            response = requests.get(paginated_url, headers=headers)
            # print(response.url)
            if response.status_code == 200:
                pagedata = response.json()  
                
                # Append data from the current page to the list
                outdata.extend(pagedata.get(paged_type, []))
    
                # Check if there are more pages
                if page >= pagedata.get("pages", 1):
                    break  # Exit the loop if we've reached the last page
    
                page += 1  # Move to the next page
                # print(f"paging page{page}")
            else:
                print("Failed to fetch campaigns. Status code:", response.status_code)
                break
    else:
        print(f"Request URL is {url}")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            outdata= response.json()
        else:
            print("Failed to fetch campaigns. Status code:", response.status_code)
    return outdata


def write_outfile(data, filename, subpath=None):
    global export_dir
    out_dir = export_dir
    if subpath: 
        out_dir = "/".join([export_dir,subpath])
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    filename = sanitize_filename(filename)
    path = os.path.join(out_dir, filename)
    print(f"export path is: {path}")
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved.")


def sanitize_filename(filename):
    # Define a regex pattern to match illegal characters
    legal_pattern = r'[^\w\-.]'
    # Replace illegal characters with an underscore
    sanitized_filename = re.sub(legal_pattern, '_', filename)
    
    # Remove all dashes
    filename = sanitized_filename.replace('-', '')
    # Remove double underscores
    filename = re.sub(r'__+', '_', filename)
    # Remove periods followed by underscores
    filename = re.sub(r'\._+', '.', filename)
    return filename


def get_tk_campaigns(user_id):
    campaign_list = get_campaign_list(user_id)
    # for cam in campaign_list[:1]:
    for cam in campaign_list:
        cid, cname = cam
        get_campaign(cid, cname)
    print("All campaigns downloaded. Process complete")
    return campaign_list
    

def get_campaign_list(user_id):
    req = fr"/api_v0/users/{user_id}/campaigns"
    cam_data = get_tk_data(req)
    filename = f"index_campaign_list_user_{user_id}.json"
    write_outfile(cam_data, filename)
    return [(cam['id'], cam['name']) for cam in cam_data['campaigns']]
              

def get_campaign(cid, cname):
    cam_subpath = sanitize_filename("_".join([str(cid), cname]))
    rp_list = get_roleplay_list(cid, cname, cam_subpath)
    dis_list = get_discussion_list(cid, cname, cam_subpath)
    for rpid in rp_list:
    # for rpid in rp_list[:5]:       
        print(f"Getting roleplay {rpid} for campaign {cid}.")
        get_roleplay(rpid, cam_subpath)
    print("Roleplays Complete")
    for did in dis_list:
    # for did in dis_list[:5]:
        print(f"Getting discussion {did} for campaign {cid}")
        get_discussion(did, cid, cam_subpath)
    print(f"Campaign {cid} complete")
    # return rp_list
    # return rp_data


def get_character_list(uid):
    req_char = f'/api_v0/users/{uid}/characters'
    char_lists = [get_tk_data(req_char, 'characters'),
                  get_tk_data(req_char + "?archived=true", 'characters')
                 ]
    char_list = char_lists[0] + char_lists[1]
    filename = f"index_char_list_user_{user_id}.json"
    write_outfile(char_list, filename, "characters")
    return [[char['id'] for char in char_list], 
            [char['name'] for char in char_list]
           ]

def get_tk_characters(uid):
    list_char_id, list_char_nm = get_character_list(uid)
    for char in zip(list_char_id, list_char_nm):
        cid, name = char
        print(f"Fetching character {cid} {name}")
        req = f'/api_v0/characters/{cid}'
        char_data = get_tk_data(req)
        if not char_data:
            continue
        dirname = sanitize_filename(f"{cid}_{name}")
        char_subpath = f"characters/{dirname}"
        filename = dirname + ".json"
        write_outfile(char_data, filename, char_subpath)

        portrait_url = char_data['image_url']
        if portrait_url:
            r = requests.get(portrait_url, stream=True)
            if r.status_code !=200:
                print(r.status_code, 'portrait download failed')
                continue
            path_portrait = os.path.join(export_dir + "/" + char_subpath, dirname + ".jpg")
            with open(path_portrait, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            print("No portrait url.")
    print("Character download is complete.")
        
        
def get_roleplay_list(cid, cname, cam_path):
    cam_path = cam_path + "/roleplays"
    print(f'Fetching roleplay list for campaign {cid}.')
    req = fr"/api_v0/campaigns/{cid}/roleplays"
    rp_data = get_tk_data(req, 'roleplays')
    filename = f"index_roleplay_list_campaign_{cid}_{cname}.json"
    write_outfile(rp_data, filename, cam_path)
    return [rp['id'] for rp in rp_data]


def get_discussion_list(cid, cname, cam_path):
    cam_path = cam_path + "/discussions"
    print(f'Fetching discussion list for campaign {cid}.')
    req = fr"/api_v0/campaigns/{cid}/discussions"
    dis_data = get_tk_data(req, 'discussions')
    filename = f"index_discussion_list_campaign_{cid}_{cname}.json"
    write_outfile(dis_data, filename, cam_path)
    return [dis['id'] for dis in dis_data]


def get_discussion(did, cid, cam_path):
    cam_path = cam_path + "/discussions"
    req_dis_data = fr'/api_v0/campaigns/{cid}/discussions/{did}'
    req_dis_comm = fr'/api_v0/campaigns/{cid}/discussions/{did}/comments'
    dis_data = get_tk_data(req_dis_data)
    dis_comm = get_tk_data(req_dis_comm, 'comments')
    dis_data['comments'] = dis_comm
    fname = f"discussion_{did}_{dis_data['name']}.json"
    write_outfile(dis_data, fname, cam_path)
    return dis_data
    

def get_roleplay(rid, cam_path):
    cam_path = cam_path + "/roleplays"
    req_rp_data = fr"/api_v0/roleplays/{rid}"
    req_rp_msgs = fr"/api_v0/roleplays/{rid}/messages"
    print("Getting Scene Data") 
    rp_data = get_tk_data(req_rp_data)
    print("Getting Message Data")
    rp_msgs = get_tk_data(req_rp_msgs, 'messages')
    rp_data['messages'] = rp_msgs
    print("Fetching Comments for Messages")
    for msg in rp_data['messages']:
        if msg['comment_count'] > 0:
            mid = str(msg['id'])
            req = fr'/api_v0/roleplays/{rid}/messages/{mid}/comments'
            comments = get_tk_data(req, 'comments')
            msg['comments'] = comments
    fname = f"roleplay_{rid}_{rp_data['name']}.json"
    write_outfile(rp_data, fname, cam_path)
    return rp_data


get_tk_characters(user_id)
get_tk_campaigns(user_id)

