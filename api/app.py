import yaml
import urllib3
import json
from requests import Session
from requests.auth import HTTPBasicAuth
import argparse
urllib3.disable_warnings()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-location", help="location of infoblox",  required=True)
    parser.add_argument("-members", help="list of DNS members",  required=True)
    parser.add_argument("-servers", help="list of Name Servers",  required=True)
    parser.add_argument("-domains", help="list of FQDN Entries",  required=True)
    args = parser.parse_args()

    base_url = f'https://{args.location}/wapi/v2.7/'

    functions = {
        'dig': 'grid?_function=query_fqdn_on_member'
    }

    username = 'admin'
    password = 'C!sco123'

    session = Session()
    session.auth=HTTPBasicAuth(username, password)
    session.verify = False
    results = {}
    members = []
    domains = []
    servers = []
    with open(args.servers, 'r') as f:
        servers = f.read().splitlines()

    with open(args.members, 'r') as f:
        members = f.read().splitlines()

    with open(args.domains, 'r') as f:
        domains = f.read().splitlines()


    for member in members:
        member_data = results.get(member, None)

        if member_data is None:
            results[member] = {}

        for server in servers:
            server_data = results[member].get(server, None)

            if server_data is None:
                results[member][server] = {}

            for fqdn in domains:
                data = {"fqdn" : fqdn,"member": member, 'name_server': server}

                resp = session.post(f'{base_url}{functions["dig"]}', json=data)
                formatted_resp = resp.json()

                error = formatted_resp.get('Error', None)

                if error: 
                    results[member][server].update({
                    fqdn: formatted_resp.get('text')
                })
                else: 
                    print(formatted_resp)
                    results[member][server].update({
                    fqdn: 'Pass'
                })

    with open('domain_output.json', 'w') as f:
        json.dump(results, f)
    # print(json.dumps(results,indent=4))
            
if __name__ == '__main__':
    main()
