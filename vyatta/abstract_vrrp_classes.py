#!/usr/bin/python3

# Copyright (c) 2019-2020 AT&T Intellectual Property.
# All rights reserved.
# SPDX-License-Identifier: GPL-2.0-only

from abc import ABC, abstractmethod

class ConfigFile(ABC):

    @abstractmethod
    def update(self, new_config):
        raise NotImplementedError

    @abstractmethod
    def write_config(self):
        raise NotImplementedError

    @abstractmethod
    def read_config(self):
        raise NotImplementedError

    @abstractmethod
    def convert_to_vci_format(self, config_string):
        raise NotImplementedError
