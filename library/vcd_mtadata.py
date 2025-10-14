# library/vcd_metadata.py
from ansible.module_utils.basic import AnsibleModule
from pyvcloud.vcd.client import BasicLoginCredentials, Client
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC

def main():
    argument_spec = dict(
        host=dict(required=True, type='str'),
        user=dict(required=True, type='str'),
        password=dict(required=True, type='str', no_log=True),
        org=dict(required=True, type='str'),
        api_version=dict(required=True, type='str'),
        verify_ssl_certs=dict(required=False, type='bool', default=False),
        target_type=dict(required=True, type='str', choices=['vdc', 'org', 'vapp']),
        target_name=dict(required=True, type='str'),
        key=dict(required=True, type='str'),
        value=dict(required=True, type='str'),
        type=dict(required=False, type='str', default='STRING'),
        state=dict(required=False, type='str', choices=['present', 'absent'], default='present'),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    try:
        client = Client(module.params['host'], verify_ssl_certs=module.params['verify_ssl_certs'], api_version=module.params['api_version'])
        client.set_credentials(BasicLoginCredentials(module.params['user'], module.params['org'], module.params['password']))

        if module.params['target_type'] == 'vdc':
            org_resource = client.get_org_by_name(module.params['org'])
            org = Org(client, resource=org_resource)
            vdc_resource = org.get_vdc(module.params['target_name'])
            vdc = VDC(client, resource=vdc_resource)
            if module.params['state'] == 'present':
                vdc.add_metadata(module.params['key'], module.params['value'], module.params['type'])
                module.exit_json(changed=True, msg=f"Metadata {module.params['key']} añadida al VDC {module.params['target_name']}")
            else:
                vdc.remove_metadata(module.params['key'])
                module.exit_json(changed=True, msg=f"Metadata {module.params['key']} eliminada del VDC {module.params['target_name']}")

        else:
            module.fail_json(msg="Solo se soporta target_type=vdc por ahora")

    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == "__main__":
    main()
