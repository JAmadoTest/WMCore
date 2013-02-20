#!/usr/bin/env python
"""
_SiteDBClient_

Emulating SiteDB
"""

class SiteDBJSON(object):
    """
    API for dealing with retrieving information from SiteDB
    """
    _people_data = [{'dn' : '/C=UK/O=eScience/OU=Bristol/L=IS/CN=simon metson',
                     'username' : 'metson'},
                    {'dn' : "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=liviof/CN=472739/CN=Livio Fano'",
                     'username' : 'liviof'}]

    _sitenames_data = [{u'site_name': u'FNAL', u'type': u'cms', u'alias': u'T1_US_FNAL'},
                       {u'site_name': u'FNAL', u'type': u'phedex', u'alias': u'T1_US_FNAL_Buffer'},
                       {u'site_name': u'FNAL', u'type': u'phedex', u'alias': u'T1_US_FNAL_MSS'},
                       {u'site_name': u'RAL', u'type': u'cms', u'alias': u'T1_UK_RAL'}]

    _siteresources_data = [{u'type': u'CE', u'site_name': u'RAL', u'fqdn': u'lcgce11.gridpp.rl.ac.uk', u'is_primary': u'n'},
                           {u'type': u'CE', u'site_name': u'RAL', u'fqdn': u'lcgce10.gridpp.rl.ac.uk', u'is_primary': u'n'},
                           {u'type': u'SE', u'site_name': u'RAL', u'fqdn': u'srm-cms.gridpp.rl.ac.uk', u'is_primary': u'n'},
                           {u'type': u'CE', u'site_name': u'RAL', u'fqdn': u'lcgce02.gridpp.rl.ac.uk', u'is_primary': u'n'},
                           {u'type': u'CE', u'site_name': u'FNAL', u'fqdn': u'cmsosgce2.fnal.gov', u'is_primary': u'n'},
                           {u'type': u'CE', u'site_name': u'FNAL', u'fqdn': u'cmsosgce4.fnal.gov', u'is_primary': u'n'},
                           {u'type': u'CE', u'site_name': u'FNAL', u'fqdn': u'cmsosgce.fnal.gov', u'is_primary': u'n'},
                           {u'type': u'SE', u'site_name': u'FNAL', u'fqdn': u'cmssrm.fnal.gov', u'is_primary': u'n'}]

    def __init__(self, config={}):
        pass

    def _people(self, username=None, clearCache=False):
        return self._people_data

    def _sitenames(self, sitename=None, clearCache=False):
        return self._sitenames_data

    def _siteresources(self, clearCache=False):
        return self._siteresources_data

    def dnUserName(self, dn):
        """
        Convert DN to Hypernews name. Clear cache between trys
        in case user just registered or fixed an issue with SiteDB
        """
        try:
            userinfo = filter(lambda x: x['dn']==dn, self._people())[0]
            username = userinfo['username']
        except (KeyError, IndexError):
            userinfo = filter(lambda x: x['dn']==dn, self._people(clearCache=True))[0]
            username = userinfo['username']
        return username

    def cmsNametoCE(self, cmsName):
        """
        Convert CMS name to list of CEs
        """
        sitenames = filter(lambda x: x['type']=='cms' and x['alias']==cmsName, self._sitenames())[0]
        siteresources = filter(lambda x: x['site_name']==sitenames['site_name'], self._siteresources())
        ceList = filter(lambda x: x['type']=='CE', siteresources)
        ceList = map(lambda x: x['fqdn'], ceList)
        return ceList

    def cmsNametoSE(self, cmsName):
        """
        Convert CMS name to list of SEs
        """
        sitenames = filter(lambda x: x['type']=='cms' and x['alias']==cmsName, self._sitenames())[0]
        siteresources = filter(lambda x: x['site_name']==sitenames['site_name'], self._siteresources())
        seList = filter(lambda x: x['type']=='SE', siteresources)
        seList = map(lambda x: x['fqdn'], seList)
        return seList

    def getAllSENames(self):
        """
        _getAllSENames_

        Get all SE names from SiteDB
        This is so that we can easily add them to ResourceControl
        """
        siteresources = self._siteresources()
        seList = filter(lambda x: x['type']=='SE', siteresources)
        seList = map(lambda x: x['fqdn'], seList)
        return seList

    def getAllCMSNames(self):
        """
        _getAllCMSNames_

        Get all the CMSNames from siteDB
        This will allow us to add them in resourceControl at once
        """
        sitenames = self._sitenames()
        cmsnames = filter(lambda x: x['type']=='cms', sitenames)
        cmsnames = map(lambda x: x['alias'], cmsnames)
        return cmsnames

    def cmsNametoList(self, cmsName, kind, file):
        if kind=='CE':
            return cmsNametoCE(cmsName)
        elif kind=='SE':
            return cmsNametoSE(cmsName)
        else:
            raise NotImplemented('cmsNametoList for kind: %s is not yet implemented' % (kind))

    def seToCMSName(self, se):
        """
        Convert SE name to the CMS Site they belong to
        """
        siteresources = filter(lambda x: x['fqdn']==se, self._siteresources())[0]
        cmsname = filter(lambda x: x['type']=='cms', self._sitenames(sitename=siteresources['site_name']))[0]['alias']
        return cmsname

    def cmsNametoPhEDExNode(self, cmsName):
        """
        Convert CMS name to list of Phedex Nodes
        """
        sitenames = self._sitenames()
        sitename = filter(lambda x: x['type']=='cms' and x['alias']==cmsName, sitenames)[0]['site_name']
        phedexnames = filter(lambda x: x['type']=='phedex' and x['site_name']==sitename, sitenames)
        phedexnames = map(lambda x: x['alias'], phedexnames)
        return phedexnames


    def phEDExNodetocmsName(self, node):
        """
        Convert PhEDEx node name to cms site
        """
        # api doesn't work at the moment - so reverse engineer
        # first strip special endings and check with cmsNametoPhEDExNode
        # if this fails (to my knowledge no node does fail) do a full lookup
        name = node.replace('_MSS',
                            '').replace('_Buffer',
                                        '').replace('_Export', '')

        return name
