from genie.conf import Genie
from genie.libs.parser.iosxe.show_ip_route import ShowIpRoute

testbed = Genie.init('default_testbed.yaml')

ios1 = testbed.devices['iosv-1']

ios1.connect()

parsed = ShowIpRoute(ios1).parse(protocol='bgp', ip='ip')

import pprint

pprint.pprint(parsed)

ios1.disconnect()
