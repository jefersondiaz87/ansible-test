from ansible.module_utils.basic import AnsibleModule
from pyvcloud.vcd.client import Client, BasicLoginCredentials

class VcdAnsibleModule(AnsibleModule):
    def __init__(self, *args, **kwargs):
        super(VcdAnsibleModule, self).__init__(*args, **kwargs)

        self.user = self.params.get('user')
        self.password = self.params.get('password')
        self.host = self.params.get('host')
        self.org = self.params.get('org', 'System')
        self.api_version = self.params.get('api_version', '37.0')
        self.verify_ssl_certs = self.params.get('verify_ssl_certs', False)

        self.client = Client(
            uri=f"https://{self.host}/api",
            api_version=self.api_version,
            verify_ssl_certs=self.verify_ssl_certs,
            log_file=None,
            log_requests=False,
            log_headers=False,
            log_bodies=False,
        )

        self.client.set_credentials(
            BasicLoginCredentials(self.user, self.org, self.password)
        )

    def execute_task(self, task):
        return self.client.get_task_monitor().wait_for_success(task)
