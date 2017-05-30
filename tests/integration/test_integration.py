"""
Start up the actual daemon and test some non blockchain commands here
"""

from jsonrpc.proxy import JSONRPCProxy
import json
import subprocess
import unittest
import time
import os

from urllib2 import URLError
from httplib import BadStatusLine
from socket import error


def shell_command(command):
    FNULL = open(os.devnull, 'w')
    p = subprocess.Popen(command,shell=False,stdout=FNULL,stderr=subprocess.STDOUT)

def lbrynet_cli(commands):
    cli_cmd=['lbrynet-cli']
    for cmd in commands:
        cli_cmd.append(cmd)
    p = subprocess.Popen(cli_cmd,shell=False,stdout=subprocess.PIPE)
    out,err = p.communicate()
    return out,err

lbrynet_rpc_port = '5279'
lbrynet = JSONRPCProxy.from_url("http://localhost:{}/lbryapi".format(lbrynet_rpc_port))


class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        shell_command(['lbrynet-daemon'])
        start_time = time.time()
        STARTUP_TIMEOUT = 180
        while time.time() - start_time < STARTUP_TIMEOUT:
            try:
                status = lbrynet.status()
            except (URLError,error,BadStatusLine) as e:
                pass
            else:
                if status['is_running'] == True:
                    return
            time.sleep(1)
        raise Exception('lbrynet daemon failed to start')

    @classmethod
    def tearDownClass(cls):
        shell_command(['lbrynet-cli', 'daemon_stop'])

    def test_cli(self):
        help_out,err = lbrynet_cli(['help'])
        self.assertTrue(help_out)

        out,err = lbrynet_cli(['-h'])
        self.assertEqual(out, help_out)

        out,err = lbrynet_cli(['--help'])
        self.assertEqual(out, help_out)

        out,err = lbrynet_cli(['status'])
        out = json.loads(out)
        self.assertTrue(out['is_running'])

    def test_status(self):
        out = lbrynet.status()
        self.assertTrue(out['is_running'])

if __name__ =='__main__':
    unittest.main()