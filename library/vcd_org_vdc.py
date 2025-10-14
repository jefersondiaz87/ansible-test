#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Módulo Ansible: vcd_org_vdc
# Crea, actualiza o elimina un OrgVDC en VMware vCloud Director
#
# Compatible con Ansible 2.15+ y VMware vCD 10.x (API clásica)
#

from ansible.module_utils.basic import AnsibleModule
from pyvcloud.vcd.client import Client, BasicLoginCredentials
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.system import System
from pyvcloud.vcd.exceptions import EntityNotFoundException

def login_to_vcd(module):
    host = module.params['host']
    org = module.params['org']
    user = module.params['user']
    password = module.params['password']
    api_version = module.params['api_version']
    verify_ssl = module.params['verify_ssl_certs']

    client = Client(host,
                    api_version=api_version,
                    verify_ssl_certs=verify_ssl,
                    log_file=None,
                    log_requests=False,
                    log_headers=False,
                    log_bodies=False)
    client.set_credentials(BasicLoginCredentials(user, org, password))
    return client

def create_org_vdc(module, client):
    vdc_name = module.params['vdc_name']
    vdc_org_name = module.params['vdc_org_name']
    provider_vdc_name = module.params['provider_vdc_name']
    network_pool_name = module.params['network_pool_name']
    allocation_model = module.params['allocation_model']
    description = module.params['description']

    cpu_allocated = module.params['cpu_allocated']
    mem_allocated = module.params['mem_allocated']

    sys = System(client)
    org = sys.get_org(vdc_org_name)

    try:
        org.get_vdc(vdc_name)
        module.exit_json(changed=False, msg=f"El VDC '{vdc_name}' ya existe.")
    except EntityNotFoundException:
        pass

    pvdc = sys.get_provider_vdc(provider_vdc_name)
    npool = sys.get_network_pool(network_pool_name)

    result = org.create_org_vdc(
        name=vdc_name,
        provider_vdc_name=provider_vdc_name,
        network_pool_name=network_pool_name,
        allocation_model=allocation_model,
        description=description,
        is_thin_provision=module.params['is_thin_provision'],
        uses_fast_provisioning=module.params['uses_fast_provisioning'],
        cpu_allocated=cpu_allocated,
        mem_allocated=mem_allocated,
        is_enabled=module.params['is_enabled']
    )

    module.exit_json(changed=True, msg=f"OrgVDC '{vdc_name}' creado correctamente.", details=result.get('href'))

def delete_org_vdc(module, client):
    vdc_name = module.params['vdc_name']
    vdc_org_name = module.params['vdc_org_name']

    sys = System(client)
    org = sys.get_org(vdc_org_name)

    try:
        vdc_resource = org.get_vdc(vdc_name)
    except EntityNotFoundException:
        module.exit_json(changed=False, msg=f"El VDC '{vdc_name}' no existe.")
    
    task = org.delete_vdc(vdc_name)
    module.exit_json(changed=True, msg=f"OrgVDC '{vdc_name}' eliminado.", details=task.get('href'))

def main():
    argument_spec = dict(
        user=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        host=dict(type='str', required=True),
        org=dict(type='str', required=True),
        api_version=dict(type='str', default='37.1'),
        verify_ssl_certs=dict(type='bool', default=False),

        vdc_name=dict(type='str', required=True),
        vdc_org_name=dict(type='str', required=True),
        provider_vdc_name=dict(type='str', required=True),
        network_pool_name=dict(type='str', required=True),
        allocation_model=dict(type='str', default='AllocationPool'),
        description=dict(type='str', default=''),
        cpu_allocated=dict(type='int', default=10000),
        mem_allocated=dict(type='int', default=4096),
        is_enabled=dict(type='bool', default=True),
        is_thin_provision=dict(type='bool', default=True),
        uses_fast_provisioning=dict(type='bool', default=True),

        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    try:
        client = login_to_vcd(module)
        if module.params['state'] == 'present':
            create_org_vdc(module, client)
        else:
            delete_org_vdc(module, client)
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

if __name__ == '__main__':
    main()
