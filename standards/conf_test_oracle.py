#!/usr/bin/env python

from WMQuality.Test import Test

from WMCore_t.Agent_t.Configuration_t import ConfigurationTest
from WMCore_t.FwkJobReport_t.FileInfo_t import FileInfoTest
from WMCore_t.FwkJobReport_t.FJR_t import FJRTest
from WMCore_t.Trigger_t.Trigger_t import TriggerTest
from WMCore_t.WMException_t import WMExceptionTest
from WMCore_t.WMFactory_t.WMFactory_t import WMFactoryTest


tests = [\
     (FileInfoTest(), 'evansde'),\
     (FJRTest(), 'evansde'),\
     (TriggerTest(),'fvlingen'),\
     (WMFactoryTest(), 'fvlingen'),\
     (WMExceptionTest(),'fvlingen'),\
     (ConfigurationTest(),'fvlingen'),\
    ]

test = Test(tests)
test.run()
test.summaryText()
        
