#!/usr/local/bin/python2.7
import argparse
import os
import sys

import netifaces
import json

EXCLUDE_WAIT_CONFIG_FILE = ('EXCLUDE_WAIT=yes\n')
NO_IPV6_CONFIG_FILE = ('NETWORKING_IPV6=no\n'
                         'IPV6INIT=no\n'
                         'DHCPV6C=no\n')
INTERFACE_CONFIG_FILE = ('DEVICE={0}\n'
                         'TYPE=Ethernet\n'
                         'ONBOOT=yes\n'
                         'BOOTPROTO=none\n')
DPDK_INTERFACE_CONFIG_FILE = ('DEVICE={0}\n'
                              'TYPE=Ethernet\n'
                              'ONBOOT=no\n'
                              'BOOTPROTO=none\n')
DHCP_INTERFACE_CONFIG_FILE = ('DEVICE={0}\n'
                                'TYPE=Ethernet\n'
                                'ONBOOT=yes\n'
                                'BOOTPROTO=dhcp\n')
MASTER_INTERFACE_CONFIG_FILE = ('DEVICE={0}\n'
                                'TYPE=Ethernet\n'
                                'ONBOOT=yes\n'
                                'BOOTPROTO=none\n'
                                'BONDING_OPTS="mode=1"\n')
SLAVE_INTERFACE_CONFIG_FILE = ('DEVICE={0}\n'
                               'TYPE=Ethernet\n'
                               'ONBOOT=yes\n'
                               'BOOTPROTO=none\n'
                               'MASTER={1}\n'
                               'SLAVE=yes\n')
VLAN_INTERFACE_CONFIG_FILE = ('DEVICE={0}.{1}\n'
                              'TYPE=Ethernet\n'
                              'ONBOOT=yes\n'
                              'BOOTPROTO=none\n'
                              'IPADDR={2}\n'
                              'PREFIX={3}\n'
                              'VLAN=yes\n')
INTERFACE_CONFIG_FILE_ACCESS = ('DEVICE={0}\n'
                                'TYPE=Ethernet\n'
                                'ONBOOT=yes\n'
                                'BOOTPROTO=none\n'
                                'IPADDR={1}\n'
                                'PREFIX={2}\n')
MASTER_INTERFACE_CONFIG_FILE_ACCESS = ('DEVICE={0}\n'
                                       'TYPE=Ethernet\n'
                                       'ONBOOT=yes\n'
                                       'BOOTPROTO=none\n'
                                       'BONDING_OPTS="mode=1"\n'
                                       'IPADDR={1}\n'
                                       'PREFIX={2}\n'
                                       'GATEWAY={3}\n')
INTERFACE_CONFIG_FILE_PATH = '/etc/sysconfig/network-scripts/ifcfg-{0}'
VLAN_INTERFACE_CONFIG_FILE_PATH = '/etc/sysconfig/network-scripts/ifcfg-{0}.{1}'
STATIC_ROUTE_CONFIG_FILE_PATH = '/etc/sysconfig/network-scripts/route-{0}'
STATIC_ROUTE_VLAN_CONFIG_FILE_PATH = '/etc/sysconfig/network-scripts/route-{0}.{1}'
STATIC_ROUTE_FILE = '{0} via {1}'


def decide_bond_name(param_interface_names):
    """
    Checks if the interfaces are already members of a bond, if yes - uses same bond name. If not - uses the next available bond number
    """
    bond_name = ''
    interfaces_bond_name = []
    for interface_name in param_interface_names:
        if os.path.isfile(INTERFACE_CONFIG_FILE_PATH.format(interface_name)):
            with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'r') as slave_interface_config_file:
                for line in slave_interface_config_file:
                    if 'MASTER' in line:
                        interfaces_bond_name.append(line[line.find('=') + 1:-1])
        else:
            pass
    if len(interfaces_bond_name) > 0:
        for i in xrange(0, len(interfaces_bond_name) - 1):
            if interfaces_bond_name[i] == interfaces_bond_name[i + 1]:
                pass
            else:
                raise Exception('Interfaces are not members of same bond')
        if len(interfaces_bond_name) == len(param_interface_names):
            bond_name = interfaces_bond_name[0]
        else:
            raise Exception('Some interfaces are part of bond, but some are not!')

    # If interfaces aren't already configured in bond
    elif len(interfaces_bond_name) == 0:
        num = 0
        while True:
            if os.path.isfile(INTERFACE_CONFIG_FILE_PATH.format('bond' + str(num))):
                num += 1
            else:
                bond_name = 'bond' + str(num)
                break
    return bond_name


def generate_static_route_config(device_name):
    """
    Generates static route config files, if needed
    :param device_name: name of interface or bond
    :return:
    """
    # If only one static route exists which is equal to cidr, then it's the component's own and doesn't need static route configuration
    if static_route is not None and not (len(static_route) == 1 and static_route[0] == cidr):
        if vlan_id is None:
            static_route_file = open(STATIC_ROUTE_CONFIG_FILE_PATH.format(device_name), 'w')
        else:
            static_route_file = open(STATIC_ROUTE_VLAN_CONFIG_FILE_PATH.format(device_name, vlan_id), 'w')
        for env_cidr in static_route:
            if env_cidr != cidr:
                static_route_file.write(STATIC_ROUTE_FILE.format(env_cidr, gateway))
            else:
                pass
        static_route_file.close()
    else:
        return


def create_interface_files(param_interfaces_list):
    #print param_interfaces_list
    # Create configuration files for interfaces not part of bond
    if len(param_interfaces_list) == 1:
        interface_name = param_interfaces_list[0]
        if untagged is True:
            with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'w') as interface_config_file:
                interface_config_file.write(INTERFACE_CONFIG_FILE_ACCESS.format(interface_name, ip_address, subnet_mask))
                interface_config_file.close()
                if noipv6 is True:
                    with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'a') as noipv6_interface_config_file:
                        noipv6_interface_config_file.write(NO_IPV6_CONFIG_FILE)
                        noipv6_interface_config_file.close()
                if excludewait is True:
                    with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'a') as excludewait_interface_config_file:
                        excludewait_interface_config_file.write(EXCLUDE_WAIT_CONFIG_FILE)
        # Note: DPDK interfaces can't be bonded
        elif dpdk is True:
            with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'w') as dpdk_interface_config_file:
                dpdk_interface_config_file.write(DPDK_INTERFACE_CONFIG_FILE.format(interface_name))
        elif dhcp is True:
            with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'w') as dhcp_interface_config_file:
                dhcp_interface_config_file.write(DHCP_INTERFACE_CONFIG_FILE.format(interface_name))
                dhcp_interface_config_file.close()
                if noipv6 is True:
                    with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'a') as noipv6_interface_config_file:
                        noipv6_interface_config_file.write(NO_IPV6_CONFIG_FILE)
        else:
            with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'w') as interface_config_file:
                interface_config_file.write(INTERFACE_CONFIG_FILE.format(interface_name))
            with open(VLAN_INTERFACE_CONFIG_FILE_PATH.format(interface_name, vlan_id), 'w') as vlan_interface_config_file:
                vlan_interface_config_file.write(VLAN_INTERFACE_CONFIG_FILE.format(interface_name, vlan_id, ip_address, subnet_mask))
        generate_static_route_config(interface_name)

    # Create configuration files for interfaces in bond
    if len(param_interfaces_list) > 1:
        bond_name = decide_bond_name(param_interfaces_list)
        for interface_name in param_interfaces_list:
            with open(INTERFACE_CONFIG_FILE_PATH.format(interface_name), 'w') as slave_interface_config_file:
                slave_interface_config_file.write(SLAVE_INTERFACE_CONFIG_FILE.format(interface_name, bond_name))
        if untagged is True:
            with open(INTERFACE_CONFIG_FILE_PATH.format(bond_name), 'w') as master_interface_config_file:
                master_interface_config_file.write(MASTER_INTERFACE_CONFIG_FILE_ACCESS.format(bond_name, ip_address, subnet_mask, bond_gateway))
        else:
            with open(INTERFACE_CONFIG_FILE_PATH.format(bond_name), 'w') as master_interface_config_file:
                master_interface_config_file.write(MASTER_INTERFACE_CONFIG_FILE.format(bond_name))
            with open(VLAN_INTERFACE_CONFIG_FILE_PATH.format(bond_name, vlan_id), 'w') as vlan_interface_config_file:
                vlan_interface_config_file.write(VLAN_INTERFACE_CONFIG_FILE.format(bond_name, vlan_id, ip_address, subnet_mask))
        generate_static_route_config(bond_name)


def check_noipv6(ip_address):
        num_point = ip_address.count('.')
        if num_point != 3 :
            return False
        else:
            return True

def get_subnetmask(cidr):
        return cidr.split('/')[1]

def get_name_interface(mac_addr):
        for interface in netifaces.interfaces():
            if netifaces.ifaddresses(interface)[17][0]['addr'].lower() == mac_addr.lower():
                return  interface

def check_dhcp(dhcp):
        if dhcp.upper() == "DHCP":
            return True
        else:
            return False

def main():
    if mac_addresses:
        # use dictionary comprehension to create a mac:interface dictionary.
        translation_dict = {netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']:interface for interface in netifaces.interfaces() if interface not in ('lo','bond')}
        print translation_dict
        # create interface files using list comprehension to get our interfaces for the input mac addresses.
        create_interface_files([translation_dict[mac_addresses]])
    elif interface_names:
        create_interface_files(interface_names)


if __name__ == "__main__":

    jsonfile=open("/meta.js")
    data=json.load(jsonfile)

    parser = argparse.ArgumentParser(description='Enter interfaces')

    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('-n', '--network',       metavar='networkname',    help='name network example backend_ic_net or oam_protected_net',      dest='networkname')
    parser.add_argument('-d', '--dpdk',          action='store_true',       help='is interface dpdk',                                             dest='dpdk')
    parser.add_argument('-e', '--bond_gateway',  metavar='bond_gateway',    help='bond gateway of network',           type=str,                   dest='bond_gateway')
    parser.add_argument('-w', '--exclude_wait',  action='store_true',       help='exclude wait',                                                  dest='excludewait')
    parser.add_argument('-g', '--gateway',       metavar='gateway',         help='gateway to exit to',                                            dest='gateway')
    parser.add_argument('-r', '--route',         metavar='static_route',    help='cidrs to route through',            nargs='+',                  dest='static_route')
    parser.add_argument('-v', '--vlan',          metavar='vlan_id',         help='vlan id to be configured',          type=str,                   dest='vlan_id')
    parser.add_argument('-u', '--untagged',      action='store_true',       help='is interface untagged',                                         dest='untagged')

    args = parser.parse_args()
    networkname = args.networkname
    mac_addresses = data[ networkname + "_mac"]
    ip_address = data[ networkname + "_ip_0"]
    dhcp = check_dhcp(data[ networkname + "_method"])
    cidr =  data[ networkname + "_cidr"]
    noipv6 = check_noipv6(ip_address)
    subnet_mask = get_subnetmask(cidr)
    interface_names = get_name_interface(mac_addresses)
    dpdk = args.dpdk
    vlan_id = args.vlan_id
    untagged = args.untagged
    static_route = args.static_route
    gateway = args.gateway
    excludewait = args.excludewait
    bond_gateway = args.bond_gateway

    # Prevent argument clashes
    if untagged and vlan_id or (not dhcp and not dpdk and (not untagged and not vlan_id)):
        sys.exit('Untagged interface requires --untagged flag, and no vlan id')
    if dpdk and (subnet_mask or ip_address or vlan_id):
        sys.exit('DPDK interface does not have ip address!')
    if static_route and not gateway:
        sys.exit('Static routing requires gateway')

    globals().update(args.__dict__)
    main()
