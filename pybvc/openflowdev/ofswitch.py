"""
Copyright (c) 2015

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
 - Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
-  Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
-  Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES;LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

@authors: Sergei Garbuzov
@status: Development
@version: 1.1.0

ofswitch.py: OpenFlow switch properties and methods


"""

import string
import json

from collections import OrderedDict

from pybvc.controller.openflownode import OpenflowNode
from pybvc.common.result import Result
from pybvc.common.status import OperStatus, STATUS
from pybvc.common.utils import find_key_values_in_dict
from pybvc.common.utils import replace_str_value_in_dict
from pybvc.common.utils import find_key_value_in_dict
from pybvc.common.utils import find_dict_in_list
from pybvc.common.utils import strip_none

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class OFSwitch(OpenflowNode):
    """ Class that represents an instance of 'OpenFlow Switch'
        (OpenFlow capable device). """
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, ctrl=None, name=None, dpid=None):
        """ Initializes this object properties. """
        super(OFSwitch, self).__init__(ctrl, name)
        self.dpid = dpid
        self.ports=[]
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, 
                          sort_keys=True, indent=4) 
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_switch_info(self):        
        status = OperStatus()
        info = {}
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            p1 = 'node'
            if (p1 in dictionary):
                p2 = 'flow-node-inventory:manufacturer'
                vlist = find_key_values_in_dict(dictionary, p2)
                if (len(vlist) != 0):
                    info['manufacturer'] = vlist[0]
                
                p3 = 'flow-node-inventory:serial-number'
                vlist = find_key_values_in_dict(dictionary, p3)
                if (len(vlist) != 0):
                    info['serial-number'] = vlist[0]
                
                p4 = 'flow-node-inventory:software'
                vlist = find_key_values_in_dict(dictionary, p4)
                if (len(vlist) != 0):
                    info['software'] = vlist[0]
                
                p5 = 'flow-node-inventory:hardware'
                vlist = find_key_values_in_dict(dictionary, p5)
                if (len(vlist) != 0):
                    info['hardware'] = vlist[0]
                
                p6 = 'flow-node-inventory:description'
                vlist = find_key_values_in_dict(dictionary, p6)
                if (len(vlist) != 0):
                    info['description'] = vlist[0]
                
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, info)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_features_info(self):
        status = OperStatus()
        info = {}
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            p2 = 'flow-node-inventory:switch-features'
            vlist = find_key_values_in_dict(dictionary, p2)
            if (len(vlist) != 0 and (type(vlist[0]) is dict)):
                p3 = 'flow-node-inventory:flow-feature-capability-'
                info = replace_str_value_in_dict(vlist[0], p3, '')
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, info)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ports_list(self):
        status = OperStatus()
        plist = []
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            obj = json.loads(resp.content)
            p1 = 'node'
            if(p1 in obj and isinstance(obj[p1], list)):
                vlist = obj[p1]
                p2 = 'node-connector'
                d = find_dict_in_list(vlist, p2)
                if (d != None) and isinstance(d[p2], list):
                    items = d[p2]
                    p3 = 'flow-node-inventory:port-number'
                    for item in items:
                        if(isinstance(item, dict) and item.has_key(p3)):
                            plist.append(item[p3])
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, plist)
        
    #---------------------------------------------------------------------------
    # TBD
    #---------------------------------------------------------------------------
    def get_port_brief_info(self, portnum):
        pass
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ports_brief_info(self):
        status = OperStatus()
        info = []
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            p1 = 'node-connector'
            vlist = find_key_values_in_dict(dictionary, p1)
            if (len(vlist) != 0 and (type(vlist[0]) is list)):
                try:
                    for item in vlist[0]:
                        port = {}
                        port['id'] = item['id']
                        port['number'] = item['flow-node-inventory:port-number']
                        port['name'] = item['flow-node-inventory:name']
                        port['MAC address'] = item['flow-node-inventory:hardware-address']
                        s = item['flow-node-inventory:current-feature']
                        port['current feature'] = s.upper()
                        info.append(port)
                    status.set_status(STATUS.OK)
                except () as e:
                    print "Error: " + repr(e)
                    status.set_status(STATUS.DATA_NOT_FOUND)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, info)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_modify_flow(self, flow_entry):
        status = OperStatus()
        templateUrlExt = "/table/{}/flow/{}"
        headers = {'content-type': 'application/yang.data+json'}
        if isinstance(flow_entry, FlowEntry):
            ctrl = self.ctrl
            url = ctrl.get_node_config_url(self.name)
            urlext = templateUrlExt.format(flow_entry.get_flow_table_id(),
                                           flow_entry.get_flow_id())
            url += urlext
#            print url
            payload = flow_entry.get_payload()
#            print payload 
            resp = ctrl.http_put_request(url, payload, headers)
            if(resp == None):
                status.set_status(STATUS.CONN_ERROR)
            elif(resp.content == None):
                status.set_status(STATUS.CTRL_INTERNAL_ERROR)
            elif (resp.status_code == 200):
                status.set_status(STATUS.OK)
            else:               
                status.set_status(STATUS.HTTP_ERROR, resp)                
        else:
            print "Error !!!"
            status.set_status(STATUS.MALFORM_DATA)
        
        return Result(status, resp)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def delete_flow(self, flow_table_id, flow_id):
        status = OperStatus()
        templateUrlExt = "/table/{}/flow/{}"
        ctrl = self.ctrl
        url = ctrl.get_node_config_url(self.name)        
        urlext = templateUrlExt.format(flow_table_id, flow_id)        
        url += urlext
        
        resp = ctrl.http_delete_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, None)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def delete_flows(self, flow_table_id):
        result = self.get_configured_FlowEntries(flow_table_id)
        status = result.get_status()
        if(status.eq(STATUS.OK) == True):
            data = result.get_data()
            for fe in data:
                self.delete_flow(flow_table_id, fe.get_flow_id())
        
        return Result(status, None)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_port_detail_info(self, portnum):
        status = OperStatus()
        info = {}
        templateUrlExt = "/node-connector/{}:{}"
        urlext = templateUrlExt.format(self.name, portnum)
        ctrl = self.ctrl
        url = ctrl.get_node_operational_url(self.name)
        url += urlext
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            try:
                p = 'node-connector'
                vlist = dictionary[p]
                if (len(vlist) != 0 and (type(vlist[0]) is dict)):
                    info = vlist[0]
                    status.set_status(STATUS.OK)
                else:
                    status.set_status(STATUS.DATA_NOT_FOUND)
            except () as e:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, info)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flows(self, tableid, operational=True):
        status = OperStatus()
        flows = {}
        templateUrlExt = "/flow-node-inventory:table/{}"
        urlext = templateUrlExt.format(tableid)
        ctrl = self.ctrl
        
        url = ""
        if (operational):
            url = ctrl.get_node_operational_url(self.name)
        else:
            url = ctrl.get_node_config_url(self.name)        
        url += urlext
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            try:
                p1 = 'flow-node-inventory:table'
                p2 = 'flow'
                vlist = dictionary[p1]
                if (len(vlist) != 0 and (type(vlist[0]) is dict) and (p2 in vlist[0])):
                    flows = vlist[0][p2]
                    status.set_status(STATUS.OK)
                else:
                    status.set_status(STATUS.DATA_NOT_FOUND)
            except () as e:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, flows)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_operational_flows(self, tableid):
        return self.get_flows(tableid, operational=True)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_configured_flows(self, tableid):
        return self.get_flows(tableid, operational=False)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_configured_flow(self, table_id, flow_id):
        status = OperStatus()
        flow = {}
        templateUrlExt = "/table/{}/flow/{}"
        ctrl = self.ctrl
        url = ctrl.get_node_config_url(self.name)
        urlext = templateUrlExt.format(table_id, flow_id)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            try:
                p1 = 'flow-node-inventory:flow'
                vlist = dictionary[p1]
                if (len(vlist) != 0 and (type(vlist[0]) is dict)):
                    flow = vlist[0]
                    status.set_status(STATUS.OK)
                else:
                    status.set_status(STATUS.DATA_NOT_FOUND)
            except () as e:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, flow)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_FlowEntries(self, tableid, operational=True):
        flows = [] # list of 'FlowEntry objects
        result = self.get_flows(tableid, operational)
        status = result.get_status()
        if(status.eq(STATUS.OK) == True):
            data = result.get_data()
            for item in data:
                fe = FlowEntry(flow_dict = item)
                flows.append(fe)
        
        return Result(status, flows)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_operational_FlowEntries(self, flow_table_id):
        return self.get_FlowEntries(flow_table_id, True)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_configured_FlowEntries(self, flow_table_id):
        return self.get_FlowEntries(flow_table_id, False)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_configured_FlowEntry(self, flow_table_id, flow_id):
        flowEntry = None
        result = self.get_configured_flow(flow_table_id, flow_id)
        status = result.get_status()
        if(status.eq(STATUS.OK) == True):
            d = result.get_data()
            flowEntry = FlowEntry(flow_dict = d)
        
        return Result(status, flowEntry)

#---------------------------------------------------------------------------
# 
#---------------------------------------------------------------------------
class ActionOutput():
    ''' OpenFlow 'Output' action type '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, port=None, length=None, order=None):
        self.type = 'output'
        self.order = order
        self.action = {'port': port, 'max_len': length}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def update(self, port=None, length=None, order=None):
        self.action = {'port': port, 'max_len': length}
        if(port != None):
            self.action['port'] = port
        if(length != None):
            self.action['max_len'] = length
        if(order != None):
            self.order = order
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def update_from_list(self, data):
        if(data != None and type(data) is dict and ('output_action' in data)):
            self.type = 'output'
            self.order = find_key_value_in_dict(data, 'order')
            self.action = {'port': None, 'max_len': None}
            self.action['port'] = find_key_value_in_dict(data, 'output_node_connector')
            self.action['max_len'] = find_key_value_in_dict(data, 'max_length')
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        s = ""
        p = self.action['port']
        l = self.action['max_len']
        if(p != None and l != None):
            if(p == 'CONTROLLER'):
                s = '{}:{}'.format(p, l)
            else:
                s = '{}:{}'.format(self.type, p)
        
        return s

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class FlowEntry(object):
    ''' Class for creating and interacting with OpenFlow flows '''
    _mn = "flow-node-inventory:flow"
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, flow_json=None, flow_dict=None):
        assert_msg = "[FlowEntry] either '%s' or '%s' should be used, " \
                     "not both" % ('flow_json', 'flow_dict')
        assert(((flow_json != None) and (flow_dict != None)) == False), assert_msg
        if (flow_dict != None):
            self.__init_from_dict__(flow_dict)
            return
        
        if (flow_json != None):
            self.__init_from_json__(flow_json)
            return
        
        ''' Unique identifier of this FlowEntry in the Controller's data store '''
        self.id = None
        
        ''' Opaque Controller-issued identifier '''
        self.cookie = None
        
        ''' Mask used to restrict the cookie bits that must match when the command is
            OFPFC_MODIFY* or OFPFC_DELETE*. A value of 0 indicates no restriction '''
        self.cookie_mask = None  
        
        ''' ID of the table to put the flow in '''
        self.table_id = None
        
        ''' Priority level of flow entry '''
        self.priority = None
        
        ''' Idle time before discarding (seconds) '''
        self.idle_timeout = None
        
        ''' Max time before discarding (seconds) '''
        self.hard_timeout = None
        
        ''' Modify/Delete entry strictly matching wildcards and priority '''
        self.strict = None
        
        ''' For OFPFC_DELETE* commands, require matching entries to include this as an
            output port. A value of OFPP_ANY indicates no restriction. '''
        self.out_port = None
        
        ''' For OFPFC_DELETE* commands, require matching entries to include this as an
            output group. A value of OFPG_ANY indicates no restriction '''
        self.out_group = None
        
        ''' Bitmap of OFPFF_* flags '''
        self.flags = None
        
        ''' This FlowEntry name in the FlowTable (internal Controller's inventory attribute) '''
        self.flow_name = None
        
        ''' This FlowEntry identifier in the FlowTable (internal Controller's inventory attribute) '''
        self.id = None
        
        ''' ??? (internal Controller's inventory attribute) '''
        self.installHw = None
        
        ''' Boolean flag used to enforce OpenFlow switch to do ordered message processing.
            Barrier request/reply messages are used by the controller to ensure message dependencies
            have been met or to receive notifications for completed operations. When the controller
            wants to ensure message dependencies have been met or wants to receive notifications for
            completed operations, it may use an OFPT_BARRIER_REQUEST message. This message has no body.
            Upon receipt, the switch must finish processing all previously-received messages, including
            sending corresponding reply or error messages, before executing any messages beyond the
            Barrier Request. '''
        self.barrier=None
        
        ''' Buffered packet to apply to, or OFP_NO_BUFFER. Not meaningful for OFPFC_DELETE* '''
        self.buffer_id = None
        
        '''  Flow match fields '''
        self.match = None
        
        ''' Instructions to be executed when a flow matches this flow entry match fields '''
        self.instructions = {'instruction': []}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_json__(self, s):
        if (s != None and isinstance(s, basestring)):
            self.instructions = {'instruction': []}
            js = string.replace(s, '-', '_')
            js = string.replace(js, 'opendaylight_flow_statistics:flow_statistics', 'flow_statistics')
            d = json.loads(js)
            for k, v in d.items():
                if ('match' == k):
                    match = Match(v)
                    self.add_match(match)
                elif ('instructions' == k):
                    instructions = Instructions(v)
                    self.add_instructions(instructions)
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("[FlowEntry] wrong argument type '%s'"
                            " (JSON 'string' is expected)" % type(s))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (d != None and isinstance(d, dict)):
            js = json.dumps(d)
            self.__init_from_json__(js)
        else:
            raise TypeError("[FlowEntry] wrong argument type '%s'"
                            " ('dict' is expected)" % type(d))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """ Return FlowEntry as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_payload(self):
        """ Return FlowEntry as a payload for the HTTP request body """
        s = self.to_json()
        # Convert all 'underscored' keywords to 'dash-separated' form used
        # by ODL YANG models naming conventions
        s = string.replace(s, '_', '-')
        # Following are exceptions from the common ODL rules for having all
        # multi-part keywords in YANG models being hash separated
        s = string.replace(s, 'table-id', 'table_id')
        s = string.replace(s, 'cookie-mask', 'cookie_mask')
        d1 = json.loads(s)
        d2 = strip_none(d1)
        payload = {self._mn : d2}
        return json.dumps(payload, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_ofp_oxm_syntax(self):
#        d = self.__dict__
#        print d
#        print dir(self)
#        print hasattr(self, 'cookie')
        
        odc = OrderedDict()
        
        # Flow Cookie
        v = self.get_flow_cookie()
        if (v != None):
            odc['cookie'] = hex(v)
        
        # Flow Duration
        v = self.get_duration()
        if (v != None):
            odc['duration'] = "{}s".format(v)
        
        # Flow Table ID
        v = self.get_flow_table_id()
        if (v != None):
            odc['table'] = v
        
        # Flow Counters
        v = self.get_pkts_cnt()
        if (v != None):
            odc['n_packets'] = v
        
        v = self.get_bytes_cnt()
        if (v != None):
            odc['n_bytes'] = v
        
        # Flow Timeouts
        v = self.get_flow_idle_timeout()
        if (v != None):
            odc['idle_timeout'] = v
        
        v = self.get_flow_hard_timeout()
        if (v != None):
            odc['hard_timeout'] = v
        
        # Flow Priority
        v = self.get_flow_priority()
        if (v != None):
            odc['priority'] = v
        
        sc = json.dumps(odc, separators=(',', '='))
        sc = sc.translate(None, '"{} ').replace(':','=')
        
        # Flow Match
        m = self.get_match_fields()
        if (m != None):
            odm = OrderedDict()
            
            v = m.get_in_port()
            if (v != None):
                odm['in_port'] = v
            
            v = m.get_eth_type()
            if (v != None):
                odm['eth_type'] = hex(v)
            
            v = m.get_eth_src()
            if (v != None):
                odm['eth_src'] = v
            
            v = m.get_eth_dst()
            if (v != None):
                odm['eth_dst'] = v
            
            v = m.get_vlan_id()
            if (v != None):
                odm['vlan_vid'] = v
            
            v = m.get_vlan_pcp()
            if (v != None):
                odm['vlan_pcp'] = v
            
            v = m.get_ip_proto()
            if (v != None):
                odm['ip_proto'] = v
            
            v = m.get_ip_dscp()
            if (v != None):
                odm['ip_dscp'] = v
            
            v = m.get_ip_ecn()
            if (v != None):
                odm['ip_ecn'] = v
            
            v = m.get_icmp4_type()
            if (v != None):
                odm['icmpv4_type'] = v
            
            v = m.get_icmpv4_code()
            if (v != None):
                odm['icmpv4_code'] = v
            
            v = m.get_icmpv6_type()
            if (v != None):
                odm['icmpv6_type'] = v
            
            v = m.get_icmpv6_code()
            if (v != None):
                odm['icmpv6_code'] = v
            
            v = m.get_ipv4_src()
            if (v != None):
                odm['ipv4_src'] = v
            
            v = m.get_ipv4_dst()
            if (v != None):
                odm['ipv4_dst'] = v
            
            v = m.get_ipv6_src()
            if (v != None):
                odm['ipv6_src'] = v
            
            v = m.get_ipv6_dst()
            if (v != None):
                odm['ipv6_dst'] = v
            
            v = m.get_ipv6_flabel()
            if (v != None):
                odm['ipv6_flabel'] = v
            
            v = m.get_ipv6_exh_hdr()
            if (v != None):
                odm['ipv6_exthdr'] = v
            
            v = m.get_udp_src_port()
            if (v != None):
                odm['udp_src'] = v
            
            v = m.get_udp_dst_port()
            if (v != None):
                odm['udp_dst'] = v
            
            v = m.get_tcp_src_port()
            if (v != None):
                odm['tcp_src'] = v
            
            v = m.get_tcp_dst_port()
            if (v != None):
                odm['tcp_dst'] = v
            
            v = m.get_sctp_src_port()
            if (v != None):
                odm['sctp_src'] = v
            
            v = m.get_sctp_dst_port()
            if (v != None):
                odm['sctp_dst'] = v
            
            v = m.get_arp_opcode()
            if (v != None):
                odm['arp_op'] = v
            
            v = m.get_arp_src_transport_address()
            if (v != None):
                odm['arp_spa'] = v
            
            v = m.get_arp_tgt_transport_address()
            if (v != None):
                odm['arp_tpa'] = v
            
            v = m.get_arp_src_hw_address()
            if (v != None):
                odm['arp_sha'] = v
            
            v = m.get_arp_tgt_hw_address()
            if (v != None):
                odm['arp_tpa'] = v
            
            v = m.get_mpls_label()
            if (v != None):
                odm['mpls_label'] = v
            
            v = m.get_mpls_tc()
            if (v != None):
                odm['mpls_tc'] = v
            
            v = m.get_mpls_bos()
            if (v != None):
                odm['mpls_bos'] = v
            
            v = m.get_tunnel_id()
            if (v != None):
                odm['tunnel_id'] = v
            
            v = m.get_metadata()
            if (v != None):
                odm['metadata'] = v
            
            sm = json.dumps(odm, separators=(',', '='))
            sm = sm.translate(None, '"{} ')
            sm = "matches={" + sm + "}"

        # Flow Instructions
        apply_actions_list = []
        instructions = self.get_instructions()
        for instruction in instructions:
            if instruction.is_apply_actions_type():
                output_list = []
                push_vlan_list = []
                pop_vlan_list = []
                push_mpls_list = []
                pop_mpls_list = []
                set_field_list = []
                drop_list = []
                apply_actions = instruction.get_apply_actions()
                for action in apply_actions:
                    if (isinstance(action, OutputAction)):
                        s = "output="
                        port = action.get_outport()
                        s += str(port)
                        ml = action.get_max_len()
                        if (ml != None):
                            s += ":" + str(ml)
                        output_list.append(s)
                    elif (isinstance(action, PushVlanHeaderAction)):
                        s = "push_vlan="
                        eth_type = action.get_eth_type()
                        s += str(hex(eth_type))
                        push_vlan_list.append(s)
                    elif (isinstance(action, PopVlanHeaderAction)):
                        s = "pop_vlan"
                        pop_vlan_list.append(s)
                    elif (isinstance(action, PushMplsHeaderAction)):
                        s = "push_mpls="
                        eth_type = action.get_eth_type()
                        s += str(hex(eth_type))
                        push_mpls_list.append(s)
                    elif (isinstance(action, PopMplsHeaderAction)):
                        s = "pop_mpls"
                        pop_mpls_list.append(s)
                    elif (isinstance(action, SetFieldAction)):
                        mpls_label = action.get_mpls_label()
                        if (mpls_label != None):
                            s = "set_mpls_label=%s" % mpls_label
                            set_field_list.append(s)
                        vlan_id = action.get_vlan_id()
                        if (vlan_id != None):
                            s = "set_vlan_vid=%s" % vlan_id
                            set_field_list.append(s)
                    elif (isinstance(action, DropAction)):
                        s = "drop"
                        drop_list.append(s)
                    
                apply_actions_list = pop_mpls_list + push_mpls_list + \
                                     pop_vlan_list + push_vlan_list + \
                                     set_field_list + drop_list + output_list
        
        sa = "actions={"
        actions_list = apply_actions_list
        if(actions_list):
            sa += ",".join(actions_list)
        sa += "}"
        
        res = sc + " " + sm + " " + sa
#        print res
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_table_id(self, table_id):
        self.table_id = table_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_table_id(self):
        res = None
        p = 'table_id'
        if hasattr(self, p):
            res = self.table_id
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_name(self, flow_name):
        self.flow_name = flow_name
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_name(self):
        return self.flow_name
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_id(self, flow_id):
        self.id = flow_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_id(self):
        return self.id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_install_hw(self, install_hw):
        self.installHw = install_hw
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_install_hw(self):
        return self.installHw
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_barrier(self, barrier):
        self.barrier = barrier
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_barrier(self, barrier):
        return self.barrier
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_priority(self, flow_priority):
        self.priority = flow_priority
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_priority(self):
        res = None
        p = 'priority'
        if hasattr(self, p):
            res = self.priority
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_hard_timeout(self, hard_timeout):
        self.hard_timeout = hard_timeout
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_hard_timeout(self):
        res = None
        p = 'hard_timeout'
        if hasattr(self, p):
            res =  self.hard_timeout
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_idle_timeout(self, idle_timeout):
        self.idle_timeout = idle_timeout
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_idle_timeout(self):
        res = None
        p = 'idle_timeout'
        if hasattr(self, p):
            res = self.idle_timeout
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_cookie(self, cookie):
        self.cookie = cookie
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_cookie(self):
        if hasattr(self, 'cookie'):
            return self.cookie
        else:
            return None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_cookie_mask(self, cookie_mask):
        self.cookie_mask = cookie_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_cookie_mask(self):
        return self.cookie_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_strict(self, strict):
        self.strict = strict
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_strict(self):
        return self.strict
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_duration(self):
        res = None
        p = 'flow_statistics'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            p1 = 'duration'
            v = find_key_value_in_dict(self.flow_statistics, p1)
            if (v != None and type(v) is dict):
                p2 = 'second'
                p3 = 'nanosecond'
                if (p2 in v and p3 in v):
                    s = v['second']
                    ns = v['nanosecond']
                    res = float(s*1000000000 + ns)/1000000000
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_pkts_cnt(self):
        res = None
        p = 'flow_statistics'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            p1 = 'packet_count'
            v = find_key_value_in_dict(self.flow_statistics, p1)
            if (v != None and type(v) is int):
                res = v
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_bytes_cnt(self):
        res = None
        p = 'flow_statistics'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            p1 = 'byte_count'
            v = find_key_value_in_dict(self.flow_statistics, p1)
            if (v != None and type(v) is int):
                res = v
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_instruction(self, instruction): 
        if isinstance(instruction, Instruction):
            self.instructions['instruction'].append(instruction)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('Instruction' instance is expected)" % instruction)
            
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_instructions(self):
        res = None
        p = 'instructions'
        if (hasattr(self, p)):
            attr = getattr(self, p)
            p2 = 'instruction'
            if (isinstance(attr, dict) and p2 in attr):
                res = attr[p2]
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_instructions(self, instructions):
        if isinstance(instructions, Instructions):
            l = instructions.get_instructions()
            for instruction in l:
                self.add_instruction(instruction)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('Instructions' instance is expected)" % instructions)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_match(self, match):
        if isinstance(match, Match):
            if(hasattr(self, 'match') and self.match != None):
                assert(False), "[FlowEntry] 'match' attribute is already set"
            self.match = match
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('Match' instance is expected)" % match)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_match_fields(self):
        res = None
        p = 'match'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Instructions():
    ''' 'Class representing OpenFlow flow instructions set ''' 
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        self.instructions = []
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (d != None and isinstance(d, dict)):
            self.instructions = []
            for k,v in d.items():
                if (('instruction' == k) and isinstance(v, list)):
                    for item in v:
                        if (isinstance(item, dict)):
                            inst = Instruction(d=item)
                            self.add_instruction(inst)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_instruction(self, instruction):
        self.instructions.append(instruction)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_instructions(self):
        res = None
        p = 'instructions'
        if (hasattr(self, p)):
            res = getattr(self, p)
            
        return res    

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Instruction():
    ''' Class representing an OpenFlow flow instruction '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, instruction_order=None, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        self.order = instruction_order
#  TBD      self.goto_table = {}
#  TBD      self.write_metadata = {}
#  TBD      self.write_actions = {}
        self.apply_actions = {'action': []}
#  TBD      self.clear_actions = {}
#  TBD      self.meter = {}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if(d != None and isinstance(d, dict)):
            for k,v in d.items():
                if ('apply_actions' == k):
                    self.apply_actions = {'action': []}
                    p1 = 'action'
                    if p1 in v and isinstance(v[p1], list):
                        for a in v[p1]:
                            if isinstance(a, dict):
                                p2 = 'output_action'
                                p3 = 'push_vlan_action'
                                p4 = 'pop_vlan_action'
                                p5 = 'push_mpls_action'
                                p6 = 'pop_mpls_action'
                                p7 = 'set_field'
                                p8 = 'drop_action'
                                if (p2 in a):
                                    action = OutputAction(d=a[p2]) 
                                    self.add_apply_action(action)
                                elif (p3 in a):
                                    action = PushVlanHeaderAction(d=a[p3])
                                    self.add_apply_action(action)
                                elif (p4 in a):
                                    action = PopVlanHeaderAction()
                                    self.add_apply_action(action)
                                elif (p5 in a):
                                    action = PushMplsHeaderAction(d=a[p5])
                                    self.add_apply_action(action)
                                elif (p6 in a):
                                    action = PopMplsHeaderAction()
                                    self.add_apply_action(action)
                                elif (p7 in a):
                                    action = SetFieldAction(d=a[p7])
                                    self.add_apply_action(action)
                                elif (p8 in a):
                                    action = DropAction()
                                    self.add_apply_action(action)
                                else:
                                    print "[Instruction] TBD"
                elif 'order':
                    self.order = v
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("[Instruction] wrong argument type '%s'"
                            " ('dict' is expected)" % type(d))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_apply_action(self, action):
        self.apply_actions['action'].append(action)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_apply_actions(self):
        res = None
        p = 'apply_actions'
        if (hasattr(self, p)):
            res = getattr(self, p)['action']
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_apply_actions_type(self):
        res = False
        p = 'apply_actions'
        if (hasattr(self, p)):
            res = True
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Action(object):
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None):
        self.order = order
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class OutputAction(Action):
    ''' The Output action forwards a packet to a specified OpenFlow port
        OpenFlow switches must support forwarding to physical ports, 
        switch-defined logical ports and the required reserved ports  '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=0, port=None, max_len=None, d=None):
        if(d != None):
            self.__init_from_dict__(d)
            return
        
        super(OutputAction, self).__init__(action_order)
        self.output_action = {'output_node_connector' : port, 'max_length' : max_len }
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self,d):
        if(d != None and isinstance(d, dict)):
            self.output_action = {'output_node_connector' : None, 'max_length' : None }
            for k,v in d.items():
                if ('output_node_connector' == k):
                    self.set_outport(v)
                elif ('max_length' == k):
                    self.set_max_len(v)
                else:
                    print "[OutputAction] TBD"
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_outport(self, port):
        self.output_action['output_node_connector'] = port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_outport(self):
        res = None
        p = 'output_action'
        if (hasattr(self, p)):
            res = getattr(self, p)['output_node_connector']
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_max_len(self, max_len):
        self.output_action['max_length'] = max_len
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_max_len(self):
        res = None
        p = 'output_action'
        if (hasattr(self, p)):
            v = getattr(self, p)['max_length']
            if (v != 0):
                res = v
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetQueueAction(Action):
    ''' The set-queue action sets the queue id for a packet. When the packet is
        forwarded to a port using the output action, the queue id determines 
        which queue attached to this port is used for scheduling and forwarding
        the packet. Forwarding behavior is dictated by the configuration of the
        queue and is used to provide basic Quality-of-Service (QoS) support '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, queue=None, queue_id=None):
        super(SetQueueAction, self).__init__(order)
        self.set_queue_action = {'queue': queue, 'queue_id': queue_id}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_queue(self, queue):
        self.group_action['queue'] = queue
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_group_id(self, queue_id):
        self.group_action['queue_id'] = queue_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class DropAction(Action):
    ''' There is no explicit action to represent drops. Instead, packets whose
        action sets have no output actions should be dropped. This result could
        come from empty instruction sets or empty action buckets in the
        processing pipeline, or after executing a Clear-Actions instruction '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=None):
        super(DropAction, self).__init__(action_order)
        self.drop_action = {}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class GroupAction(Action):
    ''' Process the packet through the specified group.
        The exact interpretation depends on group type. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, group=None, group_id=None):
        super(GroupAction, self).__init__(order)
        self.group_action = {'group': group, 'group_id': group_id}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_group(self, group):
        self.group_action['group'] = group
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_group_id(self, group_id):
        self.group_action['group_id'] = group_id

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetVlanIdAction(Action):
    ''' Set the 802.1q VLAN id '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, vid=None):
        super(SetVlanIdAction, self).__init__(order)
        self.set_vlan_id_action = {'vlan_id' : vid}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vid(self, vid):
        self.set_vlan_id_action['vlan_id'] = vid

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetVlanPCPAction(Action):
    ''' Set the 802.1q priority '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, vlan_pcp=None):
        super(SetVlanPCPAction, self).__init__(order)
        self.set_vlan_pcp_action = {'vlan_pcp' : vlan_pcp}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_pcp(self, vlan_pcp):
        self.set_vlan_pcp_action['vlan_pcp'] = vlan_pcp

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetVlanCfiAction(Action):
    ''' Seems to be ODL proprietary action type ???
        CFI (1-bit field) was formerly designated Canonical Format Indicator
        with a value of 0 indicating a MAC address in canonical format. It is
        always set to zero for Ethernet. CFI was used for compatibility between
        Ethernet and Token Ring networks. If a frame received at an Ethernet
        port had a CFI set to 1, then that frame would not be bridged to an
        untagged port.
        Currently renamed as Drop eligible indicator (DEI).        
        May be used separately or in conjunction with PCP to indicate
        frames eligible to be dropped in the presence of congestion. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, vlan_cfi=None):
        super(SetVlanCfiAction, self).__init__(order)
        self.set_vlan_cfi_action = {'vlan_cfi' : vlan_cfi}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_cfi(self, vlan_cfi):
        self.set_vlan_cfi_action['vlan_cfi'] = vlan_cfi

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class StripVlanAction(Action):
    ''' Strip the 802.1q header '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None):
        super(StripVlanAction, self).__init__(order)
        self.strip_vlan_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetDlSrcAction(Action):
    ''' Set Ethernet source address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, mac_addr=None):
        super(SetDlSrcAction, self).__init__(order)
        self.set_dl_src_action = {'address' : mac_addr}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_dl_src(self, mac_addr):
        self.set_dl_src_action['address'] = mac_addr

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetDlDstAction(Action):
    ''' Set Ethernet destination address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, mac_addr=None):
        super(SetDlDstAction, self).__init__(order)
        self.set_dl_dst_action = {'address' : mac_addr}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_dl_dst(self, mac_addr):
        self.set_dl_dst_action['address'] = mac_addr

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetNwSrcAction(Action):
    ''' Set IP source address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, ip_addr=None):
        super(SetNwSrcAction, self).__init__(order)
        self.set_nw_src_action = {'address' : ip_addr}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_nw_src(self, ip_addr):
        self.set_nw_src_action['address'] = ip_addr

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetNwDstAction(Action):
    ''' Set IP destination address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, ip_addr=None):
        super(SetNwDstAction, self).__init__(order)
        self.set_nw_dst_action = {'address' : ip_addr}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_nw_dst(self, ip_addr):
        self.set_nw_dst_action['address'] = ip_addr

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetTpSrcAction(Action):
    ''' Set TCP/UDP source port '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, port=None):
        super(SetTpSrcAction, self).__init__(order)
        self.set_tp_src_action = {'port' : port}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tp_src_port(self, port):
        self.set_tp_src_action['port'] = port

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetTpDstAction(Action):
    ''' Set TCP/UDP destination port '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, port=None):
        super(SetTpDstAction, self).__init__(order)
        self.set_tp_dst_action = {'port' : port}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tp_dst_port(self, port):
        self.set_tp_dst_action['port'] = port

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PushVlanHeaderAction(Action):
    ''' Push a new VLAN header onto the packet. The 'ethernet_type' is used as
        the Ethernet Type for the tag, only 0x8100 or 0x88a8 values should be
        used.  '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=None, eth_type=None, tag=None, pcp=None, cfi=None, vid=None, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        super(PushVlanHeaderAction, self).__init__(action_order)
        self.push_vlan_action = {'ethernet_type': eth_type, 'tag': tag, 'pcp': pcp, 'cfi': cfi, 'vlan_id': vid }
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (d != None and isinstance(d, dict)):
            self.push_vlan_action = {'ethernet_type': None, 'tag': None, 'pcp': None, 'cfi': None, 'vlan_id': None }
            for k,v in d.items():
                if ('ethernet_type' == k):
                    self.set_eth_type(v)
                else:
                    print "[PushVlanHeaderAction] TBD"
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, eth_type):
        self.push_vlan_action['ethernet_type'] = eth_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_eth_type(self):
        res = None
        p = 'push_vlan_action'
        if (hasattr(self, p)):
            res = getattr(self, p)['ethernet_type']
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tag(self, tag):
        self.output_action['tag'] = tag
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_pcp(self, pcp):
        self.output_action['pcp'] = pcp
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_cfi(self, cfi):
        self.output_action['cfi'] = cfi
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vid(self, vid):
        self.output_action['vlan_id'] = vid
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PopVlanHeaderAction(Action):
    ''' Pop the outer-most VLAN header from the packet '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=None):
        super(PopVlanHeaderAction, self).__init__(action_order)
        self.pop_vlan_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PushMplsHeaderAction(Action):
    ''' Push a new MPLS shim header onto the packet. The 'ethernet_type' is used
        as the Ethernet Type for the tag, only 0x8847 or 0x8848 values should be
        used. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=None, ethernet_type=None, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        super(PushMplsHeaderAction, self).__init__(action_order)
        self.push_mpls_action = {'ethernet_type': ethernet_type}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (d != None and isinstance(d, dict)):
            self.push_mpls_action = {'ethernet_type': None}
            for k,v in d.items():
                if ('ethernet_type' == k):
                    self.set_eth_type(v)
            else:
                print "[PushMplsHeaderAction] TBD"
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, eth_type):
        self.push_mpls_action['ethernet_type'] = eth_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_eth_type(self):
        res = None
        p = 'push_mpls_action'
        if (hasattr(self, p)):
            res = getattr(self, p)['ethernet_type']
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PopMplsHeaderAction(Action):
    ''' Pop the outer-most MPLS tag or shim header from the packet.
        The 'ethernet_type' is used as the Ethernet Type for the resulting packet
        (Ethernet Type for the MPLS payload). '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=0, ethernet_type=None):
        super(PopMplsHeaderAction, self).__init__(action_order)
        self.pop_mpls_action = {'ethernet_type': ethernet_type}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, eth_type):
        self.pop_mpls_action['ethernet_type'] = eth_type

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PushPBBHeaderAction(Action):
    ''' Push a new PBB service instance header (I-TAG TCI) onto the packet.
        The 'ethernet_type' is used as the Ethernet Type for the tag. Only
        Ethernet Type  0x88E7 should be used 
        PBB - Provider Backbone Bridges is an Ethernet data-plane technology
              (also known as MAC-in-MAC) that involves encapsulating an
              Ethernet datagram inside another one with new source and
              destination addresses. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0, ethernet_type=None):
        super(PushPBBHeaderAction, self).__init__(order)
        self.push_pbb_action = {'ethernet_type': ethernet_type}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, ethernet_type):
        self.push_pbb_action['ethernet_type'] = ethernet_type

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PopPBBHeaderAction(Action):
    ''' Pop the outer-most PBB service instance header (I-TAG TCI)
        from the packet
        PBB - Provider Backbone Bridges is an Ethernet data-plane technology
              (also known as MAC-in-MAC) that involves encapsulating an
              Ethernet datagram inside another one with new source and
              destination addresses. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(PopPBBHeaderAction, self).__init__(order)
        self.pop_pbb_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetMplsTTLAction(Action):
    ''' Replace the existing MPLS TTL. Only applies to packets with an existing
        MPLS shim header. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0, mpls_ttl=None):
        super(SetMplsTTLAction, self).__init__(order)
        self.set_mpls_ttl_action = {'mpls_ttl': mpls_ttl}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_ttl(self, mpls_ttl):
        self.set_mpls_ttl_action['mpls_ttl'] = mpls_ttl

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class DecMplsTTLAction(Action):
    ''' Decrement the MPLS TTL. Only applies to packets with an existing MPLS
        shim header '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(DecMplsTTLAction, self).__init__(order)
        self.dec_mpls_ttl = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetNwTTLAction(Action):
    ''' Replace the existing IPv4 TTL or IPv6 Hop Limit and update the IP
        checksum. Only applies to IPv4 and IPv6 packets. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0, ip_ttl=None):
        super(SetNwTTLAction, self).__init__(order)
        self.set_nw_ttl_action = {'nw_ttl': ip_ttl}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_ttl(self, ip_ttl):
        self.set_nw_ttl_action['nw_ttl'] = ip_ttl

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class DecNwTTLAction(Action):
    ''' Decrement the IPv4 TTL or IPv6 Hop Limit field and update the IP
        checksum. Only applies to IPv4 and IPv6 packets. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(DecNwTTLAction, self).__init__(order)
        self.dec_nw_ttl = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class CopyTTLOutwardsAction(Action):
    ''' Copy the TTL from next-to-outermost to outermost header with TTL.
        Copy can be IP-to-IP, MPLS-to-MPLS, or IP-to-MPLS. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(CopyTTLOutwardsAction, self).__init__(order)
        self.copy_ttl_out = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class CopyTTLInwardsAction(Action):
    ''' Copy the TTL from outermost to next-to-outermost header with TTL.
        Copy can be IP-to-IP, MPLS-to-MPLS, or MPLS-to-IP. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(CopyTTLInwardsAction, self).__init__(order)
        self.copy_ttl_in = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetFieldAction(Action):
    ''' The Extensible set_field action reuses the OXM encoding defined for
        matches, and enables to rewrite any header field in a single action.
        This allows any new match field, including experimenter fields, to be
        available for rewrite.
        The various Set-Field actions are identified by their field type and
        modify the values of respective header fields in the packet. While 
        not strictly required, the support of rewriting various header fields
        using Set-Field actions greatly increase the usefulness of an OpenFlow
        implementation. To aid integration with existing networks, we suggest
        that VLAN modification actions be supported. Set-Field actions should
        always be applied to the outermost-possible header (e.g. a 'Set VLAN ID'
        action always sets the ID of the outermost VLAN tag), unless the field
        type specifies otherwise. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=None, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        super(SetFieldAction, self).__init__(action_order)
        self.set_field = {'vlan_match': None, 'protocol_match_fields' : None}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self,d):
        if (d != None and isinstance(d, dict)):
            self.set_field = {'vlan_match': None, 'protocol_match_fields' : None}
            for k,v in d.items():
                if ('vlan_match' == k):
                    self.set_field[k] = VlanMatch(v)
                elif ('protocol_match_fields' == k):
                    self.set_field[k] = ProtocolMatchFields(v)
                else:
                    print "[SetFieldAction] TBD"
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "(dictionary is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_id(self, vid):
        if(self.set_field['vlan_match'] == None):
            self.set_field['vlan_match'] = VlanMatch()
        self.set_field['vlan_match'].set_vid(vid)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_vlan_id(self):
        res = None
        p = 'set_field'
        if (hasattr(self, p)):
            vm = getattr(self, p)['vlan_match']
            if (vm != None):
                res = vm.get_vid()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_label(self, mpls_label):
        if(self.set_field['protocol_match_fields'] == None):
            self.set_field['protocol_match_fields'] = ProtocolMatchFields()
        self.set_field['protocol_match_fields'].set_mpls_label(mpls_label)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_mpls_label(self):
        res = None
        p = 'set_field'
        if (hasattr(self, p)):
            pm = getattr(self, p)['protocol_match_fields']
            if (pm != None):
                res = pm.get_mpls_label()
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class FloodAction(Action):
    ''' Flood the packet along the minimum spanning tree, not including the
        incoming interface.
        The sentence 'along the minimum spanning tree' implies: flood the packet
        on all the ports that are not disabled by Spanning Tree Protocol. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(FloodAction, self).__init__(order)
        self.flood_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class FloodAllAction(Action):
    ''' Send the packet out all interfaces, not including the incoming
        interface '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(FloodAllAction, self).__init__(order)
        self.flood_all_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class HwPathAction(Action):
    ''' Seems to be ODL proprietary action type ??? '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(HwPathAction, self).__init__(order)
        self.hw_path_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SwPathAction(Action):
    ''' Seems to be ODL proprietary action type ??? '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(SwPathAction, self).__init__(order)
        self.sw_path_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class LoopbackAction(Action):
    ''' Seems to be ODL proprietary action type ???'''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(LoopbackAction, self).__init__(order)
        self.loopback_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Match(object):
    """Class that represents OpenFlow flow matching attributes """
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        ''' Ingress port. Numerical representation of in-coming port, starting at 1
            (may be a physical or switch-defined logical port) '''
        self.in_port = None
        
        ''' Physical port (in 'ofp_packet_in messages'), underlying physical port when
            packet received on a logical port) '''
        self.in_phy_port = None
        
        ''' Ethernet match fields: 
            - ethernet destination MAC address
            - ethernet source MAC address
            - ethernet type of the OpenFlow packet payload (after VLAN tags) '''
        self.ethernet_match = None
        
        ''' IPv4 source address (can use subnet mask) '''
        self.ipv4_source = None
        
        ''' IPv4 destination address (can use subnet mask) '''
        self.ipv4_destination = None
        
        ''' IP match fields:
            - Differentiated Service Code Point (DSCP). Part of the IPv4 ToS field or
              the IPv6 Traffic Class field.
            - ECN bits of the IP header. Part of the IPv4 ToS field or
              the IPv6 Traffic Class field 
            - IPv4 or IPv6 protocol number '''
        self.ip_match = None
        
        ''' IPv6 source address (can use subnet mask) '''
        self.ipv6_source = None
        
        ''' IPv6 destination address (can use subnet mask) '''
        self.ipv6_destination = None
        
        ''' The target address in an IPv6 Neighbor Discovery message '''
        self.ipv6_nd_target = None
        
        ''' The source link-layer address option in an IPv6 Neighbor Discovery message '''
        self.ipv6_nd_sll = None
        
        ''' The target link-layer address option in an IPv6 Neighbor Discovery message '''
        self.ipv6_nd_tll = None
        
        ''' IPv6 flow label '''
        self.ipv6_label = None
        
        ''' IPv6 Extension Header pseudo-field '''
        self.ipv6_ext_header = None
        
        ''' Protocol match fields:
           - The LABEL in the first MPLS shim header
           - The TC in the first MPLS shim header
           - The BoS bit (Bottom of Stack bit) in the first MPLS shim header
           - The I-SID in the first PBB service instance tag '''
        self.protocol_match_fields = None
        
        ''' UDP source port '''
        self.udp_source_port = None
        
        ''' UDP destination port '''
        self.udp_destination_port = None
        
        ''' TCP source port '''
        self.tcp_source_port = None
        
        ''' TCP destination port '''
        self.tcp_destination_port = None
        
        ''' SCTP source port '''
        self.sctp_source_port = None
        
        ''' SCTP destination port '''
        self.sctp_destination_port = None
        
        ''' ICMPv4 match fields:
            - ICMP type 
            - ICMP code '''
        self.icmpv4_match = None
        
        ''' ICMPv6 match fields
            - ICMPv6 type 
            - ICMPv6 code '''
        self.icmpv6_match = None
        
        ''' VLAN match fields:
            - VLAN-ID from 802.1Q header (the CFI bit indicate the presence of a valid VLAN-ID)
            - VLAN-PCP from 802.1Q header '''
        self.vlan_match = None
        
        ''' ARP opcode '''
        self.arp_op = None
        
        ''' Source IPv4 address in the ARP payload (can use subnet mask) '''
        self.arp_source_transport_address = None
        
        ''' Target IPv4 address in the ARP payload (can use subnet mask) '''
        self.arp_target_transport_address = None
        
        ''' Source Ethernet address in the ARP payload '''
        self.arp_source_hardware_address = None
        
        ''' Target Ethernet address in the ARP payload '''
        self.arp_target_hardware_address = None
        
        ''' Metadata associated with a logical port '''
        self.tunnel = None
        
        ''' Table metadata (used to pass information between tables) '''
        self.metadata = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if d != None and isinstance(d, dict):
            for k,v in d.items():
                if 'ethernet_match' == k:
                    self.ethernet_match = EthernetMatch(d[k])
                elif 'ip_match' == k:
                    self.ip_match = IpMatch(d[k])
                elif 'protocol_match_fields' == k:
                    self.protocol_match_fields = ProtocolMatchFields(d[k])
                elif 'icmpv4_match' == k:
                    self.icmpv4_match = IcmpMatch(d[k])
                elif 'icmpv6_match' == k:
                    self.icmpv6_match = IcmpV6Match(d[k])
                elif 'vlan_match' == k:
                    self.vlan_match = VlanMatch(d[k])
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("[Match] wrong argument type '%s'"
                            " ('dict is expected)" % type(d))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, eth_type):
        if(self.ethernet_match == None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_type(eth_type)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_eth_type(self):
        res = None
        p = 'ethernet_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), EthernetMatch)):
            em = getattr(self, p)
            res = em.get_type()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_src(self, eth_src):
        if(self.ethernet_match == None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_src(eth_src)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_eth_src(self):
        res = None
        p = 'ethernet_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), EthernetMatch)):
            em = getattr(self, p)
            res = em.get_src()
            if (res != None):
                res = res.lower()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_dst(self, eth_dst):
        if(self.ethernet_match == None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_dst(eth_dst )       
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_eth_dst(self):
        res = None
        p = 'ethernet_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), EthernetMatch)):
            em = getattr(self, p)
            res = em.get_dst()
            if (res != None):
                res = res.lower()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_id(self, vlan_id):
        if(self.vlan_match == None):
            self.vlan_match = VlanMatch()
        self.vlan_match.set_vid(vlan_id)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_vlan_id(self):
        res = None
        p = 'vlan_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), VlanMatch)):
            vm = getattr(self, p)
            res = vm.get_vid()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_pcp(self, vlan_pcp):
        if(self.vlan_match == None):
            self.vlan_match = VlanMatch()
        self.vlan_match.set_pcp(vlan_pcp)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_vlan_pcp(self):
        res = None
        p = 'vlan_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), VlanMatch)):
            vm = getattr(self, p)
            res = vm.get_pcp()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv4_src(self, ipv4_src):
        self.ipv4_source = ipv4_src
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ipv4_src(self):
        res = None
        p = 'ipv4_source'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv4_dst(self, ipv4_dst):
        self.ipv4_destination = ipv4_dst
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ipv4_dst(self):
        res = None
        p = 'ipv4_destination'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv6_src(self, ipv6_src):
        self.ipv6_source = ipv6_src
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ipv6_src(self):
        res = None
        p = 'ipv6_source'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv6_dst(self, ipv6_dst):
        self.ipv6_destination = ipv6_dst    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ipv6_dst(self):
        res = None
        p = 'ipv6_destination'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv6_flabel(self, ipv6_flabel):
        if(self.ipv6_label == None):
            self.ipv6_label = Ipv6Label()
        self.ipv6_label.set_flabel(ipv6_flabel)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ipv6_flabel(self):
        res = None
        p = 'ipv6_label'
        if (hasattr(self, p) and isinstance(getattr(self, p), Ipv6Label)):
            ipl = getattr(self, p)
            res = ipl.get_flabel()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv6_exh_hdr(self, ipv6_exthdr):
        if(self.ipv6_ext_header == None):
            self.ipv6_ext_header = Ipv6ExtHdr()
        self.ipv6_ext_header.set_exthdr(ipv6_exthdr)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ipv6_exh_hdr(self):
        res = None
        p = 'ipv6_ext_header'
        if (hasattr(self, p) and isinstance(getattr(self, p), Ipv6ExtHdr)):
            eh = getattr(self, p)
            res = eh.get_exthdr()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_dscp(self, ip_dscp):
        if(self.ip_match == None):
            self.ip_match = IpMatch()
        self.ip_match.ip_dscp = ip_dscp
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ip_dscp(self):
        res = None
        p = 'ip_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IpMatch)):
            ipm = getattr(self, p)
            res = ipm.get_ip_dscp()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_ecn(self, ip_ecn):
        if(self.ip_match == None):
            self.ip_match = IpMatch()
        self.ip_match.ip_ecn = ip_ecn
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ip_ecn(self):
        res = None
        p = 'ip_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IpMatch)):
            ipm = getattr(self, p)
            res = ipm.get_ip_ecn()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_proto(self, ip_proto):
        if(self.ip_match == None):
            self.ip_match = IpMatch()
        self.ip_match.ip_protocol = ip_proto
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ip_proto(self):
        res = None
        p = 'ip_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IpMatch)):
            ipm = getattr(self, p)
            res = ipm.get_ip_proto()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_udp_src_port(self, udp_src_port):
        self.udp_source_port = udp_src_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_udp_src_port(self):
        res = None
        p = 'udp_source_port'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_udp_dst_port(self, udp_dst_port):
        self.udp_destination_port = udp_dst_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_udp_dst_port(self):
        res = None
        p = 'udp_destination_port'
        if hasattr(self, p):
            res = getattr(self, p)
 
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tcp_src_port(self, tcp_src_port):
        self.tcp_source_port = tcp_src_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_tcp_src_port(self):
        res = None
        p = 'tcp_source_port'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tcp_dst_port(self, tcp_dst_port):
        self.tcp_destination_port = tcp_dst_port        
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_tcp_dst_port(self):
        res = None
        p = 'tcp_destination_port'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_sctp_src_port(self, sctp_port):
        self.sctp_source_port = sctp_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_sctp_src_port(self):
        res = None
        p = 'sctp_source_port'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_sctp_dst_port(self, sctp_port):
        self.sctp_destination_port = sctp_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_sctp_dst_port(self):
        res = None
        p = 'sctp_destination_port'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_icmpv4_type(self, icmpv4_type):
        if(self.icmpv4_match == None):
            self.icmpv4_match = IcmpMatch()
        self.icmpv4_match.set_type(icmpv4_type)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_icmp4_type(self):
        res = None
        p = 'icmpv4_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IcmpMatch)):
            icm = getattr(self, p)
            res = icm.get_type()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_icmpv4_code(self, icmpv4_code):
        if(self.icmpv4_match == None):
            self.icmpv4_match = IcmpMatch()
        self.icmpv4_match.set_code(icmpv4_code)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_icmpv4_code(self):
        res = None
        p = 'icmpv4_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IcmpMatch)):
            icm = getattr(self, p)
            res = icm.get_code()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_icmpv6_type(self, icmpv6_type):
        if(self.icmpv6_match == None):
            self.icmpv6_match = IcmpV6Match()
        self.icmpv6_match.set_type(icmpv6_type)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_icmpv6_type(self):
        res = None
        p = 'icmpv6_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IcmpV6Match)):
            icm = getattr(self, p)
            res = icm.get_type()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_icmpv6_code(self, icmpv6_code):
        if(self.icmpv6_match == None):
            self.icmpv6_match = IcmpV6Match()
        self.icmpv6_match.set_code(icmpv6_code)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_icmpv6_code(self):
        res = None
        p = 'icmpv6_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IcmpV6Match)):
            icm = getattr(self, p)
            res = icm.get_code()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_in_port(self, in_port):
        self.in_port = in_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_in_port(self):
        res = None
        p = 'in_port'
        if hasattr(self, p):
            res = getattr(self, p)
            if (res != None):
                res = str(res)
                res = res.rsplit(':', 1)[-1]
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_in_phy_port(self, in_phy_port):
        self.in_phy_port = in_phy_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_in_phy_port(self):
        res = None
        p = 'in_phy_port'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_opcode(self, arp_opcode):
        self.arp_op = arp_opcode
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_arp_opcode(self):
        res = None
        p = 'arp_op'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_src_transport_address(self, arp_src_tp_addr):
        self.arp_source_transport_address = arp_src_tp_addr       
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_arp_src_transport_address(self):
        res = None
        p = 'arp_source_transport_address'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_tgt_transport_address(self, arp_tgt_tp_addr):
        self.arp_target_transport_address = arp_tgt_tp_addr
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_arp_tgt_transport_address(self):
        res = None
        p = 'arp_target_transport_address'
        if hasattr(self, p):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_src_hw_address(self, arp_src_hw_addr):
        if(self.arp_source_hardware_address == None):
            self.arp_source_hardware_address = {}
        self.arp_source_hardware_address['address'] = arp_src_hw_addr
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_arp_src_hw_address(self):
        res = None
        p = 'arp_source_hardware_address'
        if hasattr(self, p):
            v = getattr(self, p)
            if (v != None):
                res = v['address']
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_tgt_hw_address(self, arp_tgt_hw_addr):
        if(self.arp_target_hardware_address == None):
            self.arp_target_hardware_address = {}
        self.arp_target_hardware_address['address'] = arp_tgt_hw_addr    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_arp_tgt_hw_address(self):
        res = None
        p = 'arp_target_hardware_address'
        if hasattr(self, p):
            v = getattr(self, p)
            if (v != None):
                res = v['address']
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_label(self, mpls_label):
        if(self.protocol_match_fields == None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_label(mpls_label)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_mpls_label(self):
        res = None
        p = 'protocol_match_fields'
        if (hasattr(self, p) and isinstance(getattr(self, p), ProtocolMatchFields)):
            pm = getattr(self, p)
            res = pm.get_mpls_label()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_tc(self, mpls_tc):
        if(self.protocol_match_fields == None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_tc(mpls_tc)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_mpls_tc(self):
        res = None
        p = 'protocol_match_fields'
        if (hasattr(self, p) and isinstance(getattr(self, p), ProtocolMatchFields)):
            pm = getattr(self, p)
            res = pm.get_mpls_tc()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_bos(self, mpls_bos):
        if(self.protocol_match_fields == None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_bos(mpls_bos)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_mpls_bos(self):
        res = None
        p = 'protocol_match_fields'
        if (hasattr(self, p) and isinstance(getattr(self, p), ProtocolMatchFields)):
            pm = getattr(self, p)
            res = pm.get_mpls_bos()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tunnel_id(self, tunnel_id):
        if(self.tunnel == None):
            self.tunnel = Tunnel()
        self.tunnel.set_id(tunnel_id)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_tunnel_id(self):
        res = None
        p = 'tunnel'
        if (hasattr(self, p) and isinstance(getattr(self, p), Tunnel)):
            t = getattr(self, p)
            res = t.get_id()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_metadata(self, metadata):
        if(self.metadata == None):
            self.metadata = Metadata()
        self.metadata.set_metadata(metadata)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_metadata(self):
        res = None
        p = 'metadata'
        if (hasattr(self, p) and isinstance(getattr(self, p), Metadata)):
            m = getattr(self, p)
            res = m.get_metadata()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_metadata_mask(self, metadata_mask):
        if(self.metadata == None):
            self.metadata = Metadata()
        self.metadata.set_metadata_mask(metadata_mask)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_metadata_mask(self):
        res = None
        p = 'metadata'
        if (hasattr(self, p) and isinstance(getattr(self, p), Metadata)):
            m = getattr(self, p)
            res = m.get_metadata_mask()
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class EthernetMatch(Match):
    ''' Ethernet specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return        
        
        self.ethernet_type = None
        self.ethernet_source = None
        self.ethernet_destination = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (d != None and isinstance(d, dict)):
            for k,v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("[Match] wrong argument type '%s'"
                            " ('dict is expected)" % type(d))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_type(self, eth_type):
        if(self.ethernet_type == None):
            self.ethernet_type = {}
        self.ethernet_type['type'] = eth_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_type(self):
        res = None
        p = 'ethernet_type'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            d = getattr(self, p)
            p1 = 'type'
            if (p1 in d):
                res = d[p1]
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_src(self, eth_src):
        if(self.ethernet_source == None):
            self.ethernet_source = {}
        self.ethernet_source['address'] = eth_src
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_src(self):
        res = None
        p = 'ethernet_source'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            d = getattr(self, p)
            p1 = 'address'
            if (p1 in d):
                res = d[p1]
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_dst(self, eth_dst):
        if(self.ethernet_destination == None):
            self.ethernet_destination = {}
        self.ethernet_destination['address'] = eth_dst
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_dst(self):
        res = None
        p = 'ethernet_destination'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            d = getattr(self, p)
            p1 = 'address'
            if (p1 in d):
                res = d[p1]
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class VlanMatch(Match):
    ''' VLAN specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return        
        
        ''' VLAN-ID from 802.1Q header '''
        self.vlan_id = None
        
        ''' VLAN-PCP from 802.1Q header '''
        self.vlan_pcp = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if d != None and isinstance(d, dict):
            for k,v in d.items():
                if ('vlan_id' == k):
                    self.vlan_id = VlanId(v)
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vid(self, vid):
        if(self.vlan_id == None):
            self.vlan_id = VlanId()            
        self.vlan_id.set_vid(vid)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_vid(self):
        res = None
        p = 'vlan_id'
        if (hasattr(self, p) and isinstance(getattr(self, p), VlanId)):
            vm =  getattr(self, p)
            res = vm.get_vid()
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_pcp(self, pcp):
        self.vlan_pcp = pcp
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_pcp(self):
        res = None
        p = 'vlan_pcp'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class VlanId(VlanMatch):
    ''' Helper subclass of VlanMatch class to help in serialization
        of VLAN ID information encoded in match rules of a flow entry '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return        
        
        ''' VLAN-ID from 802.1Q header '''
        self.vlan_id = None
        
        ''' Flag that indicates that 'vlan_id' value is set and matching is
            only for packets with VID equal to 'vlan_id' value '''
        self.vlan_id_present = False
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if d != None and isinstance(d, dict):
            for k,v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vid(self, vid):
        self.vlan_id = vid
        self.vlan_id_present = True
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_vid(self):
        res = None
        p = 'vlan_id'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class IcmpMatch(Match):
    ''' ICMPv4 specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
       
        ''' ICMP type '''
        self.icmpv4_type = None
    
        ''' ICMP code '''
        self.icmpv4_code = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if d != None and isinstance(d, dict):
            for k,v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_type(self, icmp_type):
        self.icmpv4_type = icmp_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_type(self):
        res = None
        p = 'icmpv4_type'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_code(self, icmp_code):
        self.icmpv4_code = icmp_code
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_code(self):
        res = None
        p = 'icmpv4_code'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class IcmpV6Match(Match):
    ''' ICMPv6 specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        ''' ICMPv6 type '''
        self.icmpv6_type = None
        
        ''' ICMPv6 code '''
        self.icmpv6_code = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (d != None and isinstance(d, dict)):
            for k,v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_type(self, icmpv6_type):
        self.icmpv6_type = icmpv6_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_type(self):
        res = None
        p = 'icmpv6_type'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_code(self, icmpv6_code):
        self.icmpv6_code = icmpv6_code
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_code(self):
        res = None
        p = 'icmpv6_code'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class IpMatch(Match):
    ''' IPv4 protocol specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        ''' "IP DSCP (6 bits in ToS field) '''
        self.ip_dscp = None
        
        ''' IP ECN (2 bits in ToS field) '''
        self.ip_ecn = None
        
        ''' IPv4 or IPv6 Protocol Number '''
        self.ip_protocol = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (d != None and isinstance(d, dict)):
            for k,v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_dscp(self, ip_dscp):
        self.ip_dscp = ip_dscp
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ip_dscp(self):
        res = None
        p = 'ip_dscp'
        if hasattr(self, p):
            res = getattr(self, p)
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_ecn(self, ip_ecn):
        self.ip_ecn = ip_ecn
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ip_ecn(self):
        res = None
        p = 'ip_ecn'
        if hasattr(self, p):
            res = getattr(self, p)
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_proto(self, ip_proto):
        self.ip_protocol = ip_proto
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ip_proto(self):
        res = None
        p = 'ip_protocol'
        if hasattr(self, p):
            res = getattr(self, p)
        return res
    
#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Ipv6Label(Match):
    ''' IPv6 Flow Label '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, flabel=None, flabel_mask=None):
        self.ipv6_flabel = flabel
        self.flabel_mask = flabel_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flabel(self, flabel, flabel_mask=None):
        self.ipv6_flabel = flabel
        self.flabel_mask = flabel_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flabel(self):
        res = None
        p = 'ipv6_flabel'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flabel_mask(self, flabel_mask):
        self.flabel_mask = flabel_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flabel_mask(self):
        res = None
        p = 'flabel_mask'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Ipv6ExtHdr(Match):
    ''' IPv6 Extension Header pseudo-field '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, exthdr=None, exthdr_mask=None):
        self.ipv6_exthdr = exthdr
        self.ipv6_exthdr_mask = exthdr_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_exthdr(self, exthdr, exthdr_mask=None):
        self.ipv6_exthdr = exthdr
        self.ipv6_exthdr_mask = exthdr_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_exthdr(self):
        res = None
        p = 'ipv6_exthdr'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_exthdr_mask(self, exthdr_mask):
        self.ipv6_exthdr_mask = exthdr_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_exthdr_mask(self):
        res = None
        p = 'ipv6_exthdr_mask'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class ProtocolMatchFields(Match):
    ''' Protocol match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d=None):
        if (d != None):
            self.__init_from_dict__(d)
            return
        
        ''' The LABEL in the first MPLS shim header '''
        self.mpls_label = None
        
        ''' The TC in the first MPLS shim header '''
        self.mpls_tc = None
        
        ''' The BoS bit (Bottom of Stack bit) in the first MPLS shim header '''
        self.mpls_bos = None
        
        ''' The I-SID in the first PBB service instance tag '''
        self.pbb = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (d != None and isinstance(d, dict)):
            for k,v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_label(self, mpls_label):
        self.mpls_label = mpls_label
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_mpls_label(self):
        res = None
        p = 'mpls_label'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_tc(self, mpls_tc):
        self.mpls_tc = mpls_tc
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_mpls_tc(self):
        res = None
        p = 'mpls_tc'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_bos(self, mpls_bos):
        self.mpls_bos = mpls_bos
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_mpls_bos(self):
        res = None
        p = 'mpls_bos'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Pbb(ProtocolMatchFields):
    ''' The I-SID in the first PBB service instance tag '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.pbb_isid = None
        self.pbb_mask = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_pbb_isid(self, pbb_isid):
        self.pbb_isid = pbb_isid
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_pbb_mask(self, pbb_mask):
        self.pbb_mask = pbb_mask

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class ArpSrcHwAddrMatch(Match):
    ''' ARP source hardware address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.address = None

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class ArpTgtHwAddrMatch(Match):
    ''' ARP target hardware address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.address = None

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Tunnel(Match):
    ''' Metadata associated with a logical port'''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' Metadata associated with a logical port'''
        self.tunnel_id = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_id(self, tunnel_id):
        self.tunnel_id = tunnel_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_id(self):
        res = None
        p = 'tunnel_id'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Metadata(Match):
    ''' Table metadata. Used to pass information between tables '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.metadata = None
        self.metadata_mask = None

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_metadata(self, metadata):
        self.metadata = metadata
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_metadata(self):
        res = None
        p = 'metadata'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_metadata_mask(self, metadata_mask):
        self.metadata_mask = metadata_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_metadata_mask(self):
        res = None
        p = 'metadata_mask'
        if (hasattr(self, p)):
            res = getattr(self, p)
        
        return res
    