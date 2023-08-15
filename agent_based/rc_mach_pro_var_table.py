#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Checks based on the RC-MACH-PRO MIB for controller status.
#
# Copyright (C) 2022 Curtis Bowden <curtis.bowden@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Example from SNMP data:


from .agent_based_api.v1 import (
    register,
    SNMPTree,
    exists,
    Service,
    Result,
    State,
    Metric,
)


def parse_rc_mach_pro_var_table(string_table):

    parsed = {}

    for (var_val_int, var_type, var_val_float, var_obj_name) in string_table:

        if (var_obj_name != ''):
            name = f"RC-MACH-PRO {var_obj_name}"
        else:
            continue

        if (name not in parsed):
            parsed[name] = {}

        parsed[name]['var_val_int'] = var_val_int
        parsed[name]['var_type'] = var_type
        parsed[name]['var_val_float'] = ':'.join('{:02x}'.format(ord(x), 'x') for x in var_val_float)
        parsed[name]['var_obj_name'] = var_obj_name

    return parsed


register.snmp_section(
    name='rc_mach_pro_var_table',
    detect=exists('.1.3.6.1.4.1.15255'),
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.15255.1.2.1.3.1',  # RC-MACH-PRO-MIB::variableTable
        oids=[
            '2',  # RC-MACH-PRO-MIB::variableValInt
            '3',  # RC-MACH-PRO-MIB::variableType
            '4',  # RC-MACH-PRO-MIB::variableValFloat
            '5',  # RC-MACH-PRO-MIB::variableObjName
        ],
    ),
    parse_function=parse_rc_mach_pro_var_table,
)


RC_TYPE_MAP = {

    0: 'analog',    # variable type is analog
    1: 'digital',   # variable type is digital
}


def discover_rc_mach_pro_var_table(section):
    for service in section.keys():
        yield Service(item=service)


def check_rc_mach_pro_var_table(item, section):
    if item not in section:
        return

    val_int = int(section[item]['var_val_int'])
    type = int(section[item]['var_type'])
    val_float = section[item]['var_val_float']

    summary = f"type: {RC_TYPE_MAP[type]}({type}), int: {val_int}, float: {val_float}"

    yield Result(state=State.OK, summary=summary)


register.check_plugin(
    name='rc_mach_pro_var_table',
    service_name='%s',
    discovery_function=discover_rc_mach_pro_var_table,
    check_function=check_rc_mach_pro_var_table,
)
