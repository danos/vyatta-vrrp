#! /usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only
"""
Vyatta VCI component to configure keepalived to provide VRRP functionality
"""

import re
import json
from typing import List, Union, Tuple, Any, Dict

import vyatta.abstract_vrrp_classes as AbstractConfig


class KeepalivedConfig(AbstractConfig.ConfigFile):
    """
    Implementation to convert vyatta YANG to Keepalived configuration

    This file is the concrete implementation of the VRRP abstract class
    ConfigFile for the Keepalived implementation of VRRP. It is to be used
    by the Vyatta VCI infrastructure to configure Keepalived. It does this
    by converting the YANG representation given to it into the Keepalived
    config format and writing it to the config file, it also converts
    from the config file format back to the YANG representation.

    The Vyatta VCI infrastructure sends, and expects to receive, configuration
    in a JSON 7951 format. For the simplest configured VRRP group the
    infrastructure will send the following JSON to the registered VCI unit
    which will then convert it to the shown Keepalived.conf file.

    Simplest config:
        interfaces {
            dataplane dp0p1s1 {
                address 10.10.1.1/24
                vrrp {
                    vrrp-group 1 {
                        virtual-address 10.10.1.100/25
                    }
                }
            }
        }

    VCI JSON 7951 format:
        {
            "vyatta-interfaces-v1:interfaces":{
                "vyatta-interfaces-dataplane-v1:dataplane":
                    [
                        {
                            "tagnode":"dp0p1s1",
                            "vyatta-vrrp-v1:vrrp": {
                                "start-delay": 0,
                                "vrrp-group":[
                                    {
                                        "tagnode":1,
                                        "accept":false,
                                        "preempt":true,
                                        "version":2,
                                        "virtual-address":["10.10.1.100/25"]
                                    }
                                ]
                            }
                        }
                    ]
                }
        }

    Generated Keepalived.conf file:
        #
        # autogenerated by /opt/vyatta/sbin/vyatta-vrrp-vci
        #

        global_defs {
            enable_traps
            enable_dbus
            snmp_socket tcp:localhost:705:1
            enable_snmp_keepalived
            enable_snmp_rfc
        }
        vrrp_instance vyatta-dp0p1s1-1 {
            state BACKUP
            interface dp0p1s1
            virtual_router_id 1
            version 2
            start_delay 0
            priority 100
            advert_int 1
            virtual_ipaddress {
                10.10.1.100/25
            }
        }

    These are two very different formats and contain some curiosities from
    legacy implementations that need to be maintained. Converting from
    YANG to Keepalived.conf is relatively easily with most of the work passed
    on to a VRRP group class that returns a string in the correct format.
    This class then writes all of the generated strings to the file.

    Converting from Keepalived.conf to YANG is more complex due to the flat
    structure of Keepalived.conf and the nested format of the YANG.
    The majority of this file is dedicated to this effort.

    Unit testing:
        See the README under vyatta-vrrp on how to set up the testing
        environment. If you're not familiar with pytest I recommend
        starting here https://docs.pytest.org/en/latest/example/simple.html
        once you have your environment set up.
        The test file for this class is
        vyatta-vrrp/tests/test_keepalived_config-file.py

    Acceptance testing:
        To be added.

    Regression testing:
        Use the VRRP developer regression setup, documentation for this can be
        found on the internal AT&T wiki.
    """

    def __init__(
            self,
            config_file_path: str = "/etc/keepalived/keepalived.conf"):
        """
        KeepalivedConfig constructor

        Arguments:
            config_file_path (str):
                Path to where the keepalived config file path is, defaults
                to the standard file but can be overwritten.

        Attributes:
            config_string (str):
                String to write to the config file, contains some
                autogenerated text for global defines
            config_file (str):
                Internal string for the config file path
            implementation_name (str):
                Name of the implementation that provides the VRRP support.
            vrrp_instances:
                A list of VRRP group Objects that have been found in the
                config passed to this object
                Currently this is modified in the update call, there must
                be a better way to do this
            vif_yang_name, vrrp_yang_name (str):
                Name of the YANG paths that are used for dictionary keys to
                avoid magic strings
        """

        self.config_string = """
#
# Autogenerated by /opt/vyatta/sbin/vyatta-vrrp
#


global_defs {
        enable_traps
        enable_dbus
        snmp_socket tcp:localhost:705:1
        enable_snmp_keepalived
        enable_snmp_rfc
}
    """
        self.config_file = config_file_path  # type: str
        self.vrrp_instances = []  # type: List[dict]
        self.implementation_name = "Keepalived"  # type: str

        self.interface_yang_name = \
            "vyatta-interfaces-v1:interfaces"  # type: str
        self.dataplane_yang_name = \
            "vyatta-interfaces-dataplane-v1:dataplane"  # type: str
        self.bonding_yang_name = \
            "vyatta-bonding-v1:bonding"  # type: str
        self.switchport_yang_name = \
            "vyatta-switchport-v1:switchport"  # type: str
        self.vif_yang_name = "vif"  # type: str
        self.vrrp_yang_name = "vyatta-vrrp-v1:vrrp"  # type: str

    def config_file_path(self) -> str:
        """Path to the keepalived config file returns string"""
        return self.config_file

    def impl_name(self) -> str:
        """Name of the VRRP implementation returns string"""
        return self.implementation_name

    def update(self, new_config: Dict) -> None:
        """
        Update the list of VRRP instances for the object

        Arguments:
            new_config (dictionary):
                A dictionary containing the new config passed from
                the infrastructure. Used to create VRRP group objects

        Create new VRRP group Objects from the config passed in
        and replace the vrrp_instances list with the new config
        """

    def write_config(self) -> None:
        """
        Write config to the file at config_file

        Invoke the str method for this object and write it to the config
        file provided at instantiation. If there is a problem writing the
        file an error is thrown.
        """

    def read_config(self) -> str:
        """Read config from file at config_file and return to caller"""
        config_string = ""
        with open(self.config_file, "r") as file_handle:
            config_string = file_handle.read()
        return config_string

    def convert_to_vci_format(self, config_string: str) -> str:
        """
        Given a string of keepalived config convert to YANG format

        Arguments:
            config_string:
                A string of Keepalived config, any string can be passed in but
                this string should have been retrieved using read_config
        Returns:
            A dictionary of the values found in the config string. This
            dictionary will be in the python format, before returning to the
            infrastructure it should be converted to JSON
        """

        config_lines = config_string.splitlines()  # type: List[str]
        vrrp_group_start_indexes = self._get_config_indexes(
            config_lines, "vrrp_instance")  # type: List[int]
        if vrrp_group_start_indexes == []:
            return json.dumps({})

        group_config = self._get_config_blocks(
            config_lines, vrrp_group_start_indexes)  # type: List[List[str]]

        # config_without_groups = \
        #    config_lines[:vrrp_group_start_indexes[0]]  # type: List[str]

        yang_representation = {self.interface_yang_name: {}}
        for group in group_config:

            intf_name = self._find_config_value(
                group, "interface")[1]  # type: str
            vif_number = ""
            if "." in intf_name:
                vif_sep = intf_name.split(".")
                intf_name = vif_sep[0]
                vif_number = vif_sep[1]  # type: str

            interface_list = yang_representation[self.interface_yang_name]
            # Find the interface type for the interface name, right now this
            # is just a guess, there might be a better method of doing this
            # than regexes
            if re.match(r"dp\d+bond\d+", intf_name):
                if self.bonding_yang_name not in interface_list:
                    interface_list[self.bonding_yang_name] = []
                interface_list = interface_list[self.bonding_yang_name]
            elif re.match(r"sw\d+", intf_name):
                if self.switchport_yang_name not in interface_list:
                    interface_list[self.switchport_yang_name] = []
                interface_list = interface_list[self.switchport_yang_name]
            else:
                if self.dataplane_yang_name not in interface_list:
                    interface_list[self.dataplane_yang_name] = []
                interface_list = interface_list[self.dataplane_yang_name]

            # Hackery to find the reference to the interface this vrrp
            # group should be added to.
            insertion_reference = self._find_interface_in_yang_repr(
                intf_name, vif_number, interface_list)

            # All groups should have the same start delay but check and
            # store the largest delay found
            new_group_start_delay = \
                self._find_config_value(group, "start_delay")[1]
            current_start_delay = \
                insertion_reference[self.vrrp_yang_name]["start-delay"]

            if new_group_start_delay != current_start_delay and \
               int(current_start_delay) < int(new_group_start_delay):
                insertion_reference[self.vrrp_yang_name]["start-delay"] = \
                        new_group_start_delay

            insertion_reference[self.vrrp_yang_name]["vrrp-group"].append(
                self._convert_keepalived_config_to_yang(group))

        return json.dumps(yang_representation)

    @staticmethod
    def _get_config_indexes(
            config_lines: List[str],
            search_string: str) -> List[int]:
        """
        Get index for every list entry that matches the provided search string

        Arguments:
            config_lines (List[str]):
                Keepalived config split into lines
            search_string (str):
                The term to search the lines for

        Return:
            A list of integers denoting the index where a value was found

        Example:
            test_list = ["Test", "Value", "Test", "Test", "Stop"]
            index_list = _get_config_indexes(test_list, "Test")
            print(index_list)  # [0, 2, 3]

        This function is used to find the index of each vrrp_instance, but can
        be used to find other indexes. It's useful to know where each group
        in the config starts.
        """

        stripped_lines = [x.strip() for x in config_lines]  # type: List[str]
        config_start_indices = [i for i, x in enumerate(stripped_lines)
                                if search_string in x]  # type: List[int]
        return config_start_indices

    @staticmethod
    def _get_config_blocks(
            config_list: List[str],
            indexes_list: List[int]) -> List[List[str]]:
        """
        Group lines of VRRP config into logical blocks for easier processing

        Arguments:
            config_list (List[str]):
                Flat list of keepalived config strings
            indexes_list (List[str]):
                List of integers denoting where each individual VRRP config
                block starts in config_list

        Return:
            A list of list where each entry is a logical block of VRRP group
            config
        """

        stripped_list = [x.strip() for x in config_list]  # type: List[str]
        group_list = []  # type: List[List[str]]
        for idx, start in enumerate(indexes_list):
            end = None  # type: Union[int, None]
            if idx+1 < len(indexes_list):
                end = indexes_list[idx+1]
            group_list.append(stripped_list[start:end])
        return group_list

    @staticmethod
    def _find_config_value(
            config_list: List[str],
            search_term: str) -> Tuple[bool, Union[List[None], str]]:
        """
        Find a config line in a block of config

        Arguments:
            config_list (List[str]):
                All config lines relating to a single VRRP group
            search_term (str):
                The key to look for in the config

        Return:
            Returns a tuple that can take one of three formats. The first value
            in the tuple is always a boolean. True for if the search term was
            found in the config, false and a value of "NOTFOUND" as the second
            element otherwise.
            The second value is either [None] if the search term is a presence
            indicator or the value found on the line if the search term is a
            key with configuration

        Example:
            config_block = ["vrrp_instance dp0p1s1", "priority 200",
                "use_vmac"]
            _find_config_value(config_block, "preempt")  # (False, "NOTFOUND")
            _find_config_value(config_block, "use_vmac")  # (True, [None])
            _find_config_value(config_block, "priority")  # (True, "200")
        """

        for line in config_list:
            regex_search = re.match("{}".format(search_term), line)
            if regex_search is not None:
                regex_search = re.match(f"{search_term}\s+(.*)", line)
                if regex_search is not None:
                    return (True, regex_search.group(1))
                # YANG JSON representation has single key with no value as
                # <key>: [null]
                return (True, [None])
        return (False, "NOTFOUND")

    def _find_interface_in_yang_repr(
            self,
            interface_name: str,
            vif_number: str,
            interface_list: List[Any]) -> dict:
        """
        Find the interface that a VRRP group is to be added to based on
        name of interface and any vif number

        Arguments:
            interface_name (str):
                Name of the interface found in the VRRP group config
            vif_number (str):
                Vif number for the interface, this may be ""
            interface_list (List[Any]):
                The list of interfaces for this interface's type (dataplane,
                bonding, switching, etc). The interface's type should be
                found in the caller

        Return:
            The value returned here is a dictionary representing an YANG
            interface.
        NB:
            There is a little bit of magic (read hackery) done to achieve the
            return value. This function uses (and possibly abuses) python's
            pass by assignment characteristics, effectively returning a
            reference to a dictionary inside the interface_list passed to the
            function.
            As we don't reassign interface_list inside the function it is a
            shallow copy to the data structure from the caller. It's possible
            to use this to add to that datastructure or point a new variable
            to an item inside that datastructure.
            Using this we create the interface if it doesn't exist in the list
            and then return a reference to the interface to be used to add the
            VRRP group
        """

        interface_level = None  # type: Any
        intf_dict = None  # type: Any

        # TODO: This may be better split into two functions, one for interfaces
        # and another for vifs
        if interface_list == []:
            # Interface list is empty so create the interface and add it to the
            # list and then return the reference
            intf_dict = {"tagnode": interface_name}
            interface_level = intf_dict
            interface_list.append(intf_dict)
        else:
            # Interface list has entries so we need to loop through them and
            # see if the interface already exists
            for intf in interface_list:
                if intf["tagnode"] == interface_name:
                    interface_level = intf
                    break

        if interface_level is None:
            # Interface doesn't exists yet but there are interfaces in the list
            # so create the interface and return the reference
            intf_dict = {"tagnode": interface_name}
            interface_list.append(intf_dict)
            interface_level = interface_list[-1]

        # Deal with vifs here now that we've found the interface it's on
        if vif_number != "":
            if self.vif_yang_name not in interface_level:
                vif_dict = {"tagnode": vif_number}
                interface_level[self.vif_yang_name] = [vif_dict]
                interface_level = vif_dict
            else:
                vif_exists = False
                for vif in interface_level[self.vif_yang_name]:
                    if vif["tagnode"] == vif_number:
                        vif_exists = True
                        interface_level = vif
                        break
                if not vif_exists:
                    vif_dict = {"tagnode": vif_number}
                    interface_level[self.vif_yang_name].append(vif_dict)
                    interface_level = vif_dict

        if self.vrrp_yang_name not in interface_level:
            # If there is no VRRP config in the interface yet add the top level
            # dictionary to the interface
            interface_level[self.vrrp_yang_name] = {"start-delay": 0,
                                                    "vrrp-group": []}
        return interface_level

    def _convert_keepalived_config_to_yang(
            self,
            config_block: List[str]) -> dict:
        """
        Converts a Keepalived VRRP block of config into YANG

        Arguments:
            config_block (List[str]):
                 The lines of VRRP config to be converted to the YANG
                 representation

        Return:
            A python dictionary representing the config found in the strings,
            N.B. the caller should convert this to JSON before sending it to
            the VCI infra
        """

        if config_block == []:
            return {}
        config_dict = {
            "accept": "accept",
            "preempt": "preempt",
            "priority": "priority",
            "tagnode": "virtual_router_id",
            "version": "version",
        }  # type: Any

        # Single line config code
        for key in config_dict:
            # Search for each term in the config
            config_exists = self._find_config_value(config_block,
                                                    config_dict[key])
            if not config_exists[0]:
                # Accept and preempt are required defaults in the YANG called
                # out as a special case here if they don't explicitly exist in
                # the config block
                if key == "accept":
                    config_dict[key] = False
                elif key == "preempt":
                    config_dict[key] = True
                else:
                    config_dict[key] = config_exists[1]  # NOTFOUND
            elif isinstance(config_exists[1], list):
                # Term exists in config and is presence
                config_dict[key] = config_exists[1]
            elif config_exists[1].isdigit():
                # Term exists in config and has a value
                config_dict[key] = int(config_exists[1])
            else:
                config_dict[key] = config_exists[1]
        config_dict = {k: v for k, v in config_dict.items()
                       if v != "NOTFOUND"}

        # Multi ling config code, look for the block start and then the next }
        vips_start = config_block.index('virtual_ipaddress {')  # type: int
        vips_end = config_block.index('}', vips_start)  # type: int
        config_dict["virtual-address"] = config_block[vips_start+1:vips_end]
        return config_dict
