#!/usr/bin/env python3
import json, sys
from pyvcloud.vcd.client import Client, BasicLoginCredentials
from pyvcloud.vcd.system import System

def crear_org(host, user, password, org_name, full_name):
    if not host.endswith('/api'):
        host = host.rstrip('/') + '/api'
    client = Client(host, api_version="37.1", verify_ssl_certs=False, serialization="json")
    client.set_credentials(BasicLoginCredentials(user, 'system', password))
    system = System(client)
    try:
        system.create_org(org_name, full_name, is_enabled=True)
        print(json.dumps({"status": "created", "org": org_name}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
    finally:
        client.logout()

if __name__ == "__main__":
    params = json.loads(sys.argv[1])
    crear_org(**params)
