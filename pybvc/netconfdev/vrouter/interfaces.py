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

firewall.py: Firewall specific properties and access methods


"""

import json

from pybvc.common.utils import strip_none, remove_empty_from_dict, dict_keys_underscored_to_dashed

#-------------------------------------------------------------------------------
# Class 'OpenVpnInterface'
#-------------------------------------------------------------------------------
class OpenVpnInterface():
    ''' Class representing an OpenVPN tunnel interface '''
    _mn1 = "vyatta-interfaces:interfaces"
    _mn2 = "vyatta-interfaces-openvpn:openvpn"
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, name):
        ''' OpenVPN tunnel interface name '''
        self.tagnode = name
        
        ''' Description for the interface '''
        self.description = None
        
        ''' OpenVPN authentication method (container) '''
        self.auth = None
        
        ''' Hashing algorithm option
            enumeration: 'md5', 'sha1', 'sha256', 'sha512' '''
        self.hash = None
        
        ''' Interface to be disabled '''
        self.disable = None
        
        ''' Server-mode options (container) '''
        self.server = None
        
        ''' OpenVPN interface device-type '''
        self.device_type = None
        
        ''' File containing the secret key shared with remote end of tunnel '''
        self.shared_secret_key_file = None
        
        ''' Data encryption algorithm option
            enumeration: 'des', '3des', 'bf128', 'bf256', 'aes128', 'aes192', 'aes256'  '''
        self.encryption = None
        
        ''' Additional OpenVPN options (list) '''
        self.openvpn_option = []
        
        ''' Local IP address or network address '''
        self.local_address = None
        
        ''' Local port number to accept connections (range 1..65535) '''
        self.local_port = None
        
        ''' Local IP address to accept connections (all if not set) '''
        self.local_host = None
        
        ''' IP address of remote end of tunnel '''
        self.remote_address = None
        
        ''' Remote port number to connect to '''
        self.remote_port = None
        
        ''' Remote host to connect to (dynamic if not set) '''
        self.remote_host = []
        
        ''' Transport Layer Security (TLS) options (container) '''
        self.tls = TlsOptions()
        
        ''' OpenVPN mode of operation
            enumeration: 'site-to-site', 'client', 'server' '''
        self.mode = None
        
        ''' OpenVPN tunnel to be used as the default route (container)'''
        self.replace_default_route = None
        
        ''' OpenVPN communication protocol
            enumeration: 'udp', 'tcp-passive', 'tcp-active' '''
        self.protocol = None
        
        ''' IPv4 parameters (container) '''
        self.ip = None
        
        ''' IPv6 parameters (container) '''
        self.ipv6 = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """ Return this object as a string """
        return str(vars(self))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """ Return this object as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_payload(self):
        """ Return this object as a payload for HTTP request """
        s = self.to_json()
        obj = json.loads(s)
        obj1 = strip_none(obj)
        obj2 = remove_empty_from_dict(obj1)
        obj3 = dict_keys_underscored_to_dashed(obj2)
        payload = {self._mn1: {self._mn2:[obj3]}}
        return json.dumps(payload, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mode(self, mode):
        self.mode = mode
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_shared_secret_key_file(self, path):
        self.shared_secret_key_file = path
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_local_address(self, addr):
        self.local_address = addr
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_remote_address(self, addr):
        self.remote_address = addr
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_remote_host(self, addr):
        self.remote_host.append(addr)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tls_role(self, role):
        self.tls.set_role(role)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tls_dh_file(self, path):
        self.tls.set_dh_file(path)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tls_ca_cert_file(self, path):
        self.tls.set_ca_cert_file(path)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tls_cert_file(self, path):
        self.tls.set_cert_file(path)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tls_crl_file(self, path):
        self.tls.set_crl_file(path)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tls_key_file(self, path):
        self.tls.set_key_file(path)

#-------------------------------------------------------------------------------
# Class 'TlsOptions'
#-------------------------------------------------------------------------------
class TlsOptions():
    ''' Transport Layer Security (TLS) options 
        Helper class of the 'OpenVpnInterface' class '''
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' Role in TLS negotiation
            enumeration: 'active', 'passive' '''
        self.role = None
        
        ''' File containing Diffie Hellman parameters (server only) '''
        self.dh_file = None
        
        ''' File containing certificate for Certificate Authority (CA) '''
        self.ca_cert_file = None
        
        ''' File containing certificate for this host '''
        self.cert_file = None
        
        ''' File containing certificate revocation list (CRL) for this host '''
        self.crl_file = None
        
        ''' File containing this host's private key '''
        self.key_file = None
        
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_role(self, role):
        self.role = role
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_dh_file(self, path):
        self.dh_file = path
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ca_cert_file(self, path):
        self.ca_cert_file = path
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_cert_file(self, path):
        self.cert_file = path
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_crl_file(self, path):
        self.crl_file = path
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_key_file(self, path):
        self.key_file = path
