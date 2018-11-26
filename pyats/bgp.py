from ats import aetest
from genie.libs.parser.iosxe.show_bgp import ShowBgpAllSummary
from genie.libs.parser.iosxe.show_ip_route import ShowIpRoute

import logging
import pprint
import re

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def check_topology(self,
                       testbed,
                       ios1_name = 'iosv-1',
                       ios2_name = 'iosv-2'):
        ios1 = testbed.devices[ios1_name]
        ios2 = testbed.devices[ios2_name]

        # add them to testscript parameters
        self.parent.parameters.update(ios1 = ios1, ios2 = ios2)

    @aetest.subsection
    def establish_connections(self, steps, ios1, ios2):
        with steps.start('Connecting to %s' % ios1.name):
            ios1.connect()

        with steps.start('Connecting to %s' % ios2.name):
            ios2.connect()

class BgpTestcase(aetest.Testcase):
    @aetest.test
    def check_bgp_neighbor(self):
        ios1 = self.parameters['ios1']
        bgp = ShowBgpAllSummary(ios1).parse()
        state_pfxrcd = bgp['vrf']['default']['neighbor']['192.168.12.2']['address_family']['ipv4 unicast']['state_pfxrcd']
        assert state_pfxrcd == '1', 'state/pfxrcd is {}'.format(state_pfxrcd)

    @aetest.test.loop(device=('ios1', 'ios2'), neighbor=('192.168.12.2', '192.168.12.1'))
    def check_bgp_neighbor_loop(self, device, neighbor):
        ios = self.parameters[device]
        bgp = ShowBgpAllSummary(ios).parse()
        state_pfxrcd = bgp['vrf']['default']['neighbor'][neighbor]['address_family']['ipv4 unicast']['state_pfxrcd']
        assert state_pfxrcd == '1', 'state/pfxrcd is {}'.format(state_pfxrcd)

    @aetest.test
    def check_ip_route(self):
        ios1 = self.parameters['ios1']
        route = ShowIpRoute(ios1).parse(protocol='bgp', ip='ip')
        assert '2.2.2.2/32' in route['vrf']['default']['address_family']['ipv4 unicast']['ip'], 'route missing...'
    
    @aetest.test.loop(device=('ios1','ios2'), prefix=('2.2.2.2/32', '1.1.1.1/32'))
    def check_ip_route_loop(self, device, prefix):
        ios = self.parameters[device]
        route = ShowIpRoute(ios).parse(protocol='bgp', ip='ip')
        assert prefix in route['vrf']['default']['address_family']['ipv4 unicast']['ip'], 'route missing...'
    
class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def disconnect(self, steps, ios1, ios2):
        with steps.start('Disconnecting from %s' % ios1.name):
            ios1.disconnect()

        with steps.start('Disconnecting from %s' % ios2.name):
            ios2.disconnect()

if __name__ == '__main__':
    import argparse
    from ats.topology import loader

    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest = 'testbed',
                        type = loader.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))
