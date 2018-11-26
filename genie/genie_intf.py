from genie.conf import Genie
from genie.libs.parser.iosxe.show_interface import ShowInterfaces

testbed = Genie.init('default_testbed.yaml')

ios1 = testbed.devices['iosv-1']

ios1.connect()

parsed = ShowInterfaces(ios1).parse()

import pprint

pprint.pprint(parsed)

ios1.disconnect()
