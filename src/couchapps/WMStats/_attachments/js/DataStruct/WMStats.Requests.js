WMStats.namespace("Requests");
WMStats.Requests = function (flag) {
    /*
     * Data structure for holding the request
     */
    // request data by workflow name
    var _dataByWorkflow = {};
    var _dataByWorkflowAgent = {}
    var _get = WMStats.Utils.get;
    // number of requests in the data
    var _length = 0;
    var _filter = {};
    var _filteredLength = 0;
    var _filteredRequests = flag || WMStats.Requests(true);
    
    var statusOrder = {
        "new": 1,
        "testing-approved": 2,
        "testing": 3,
        "tested": 4,
        "test-failed": 5,
        "assignment-approved": 6,
        "assigned": 7,
        "ops-hold": 8,
        "negotiating": 9,
        "acquired": 10,
        "running": 11,
        "failed": 12,
        "epic-FAILED": 13,
        "completed": 14,
        "closed-out": 15,
        "announced": 16,
        "aborted": 17,
        "rejected": 18
    }
    
    function _addJobs(baseObj, additionObj) {
       for (var field in additionObj) {
            if (!baseObj[field]) {
                baseObj[field] = additionObj[field];
            } else {
                if (typeof(baseObj[field]) == "object"){
                    _addJobs(baseObj[field], additionObj[field]);
                } else { // should be number
                    baseObj[field] += additionObj[field];
                }
            }
        } 
    }
    
    function getLength() {
        return _length;
    }
    
    function getFilter() {
        return _filter;
    }
    
    function setFilter(filter) {
        _filter = filter;
    }
    
    function updateRequest(doc) {
        var request = getDataByWorkflow(doc.workflow);
        if (!request) {
            _length++;
            _dataByWorkflow[doc.workflow] = {};
        }
        var requestWithAgent = getRequestByNameAndAgent(doc.workflow, doc.agent_url);
         
        for (var field in doc) {
            //handles when request is splited in more than one agents
            if (_dataByWorkflow[doc.workflow][field]  && (field == 'sites' || field == 'status')){
                _addJobs(_dataByWorkflow[doc.workflow][field], doc[field])
            } else {
                _dataByWorkflow[doc.workflow][field] = doc[field];
            }
            //for request, agenturl structure
            requestWithAgent[field] = doc[field];
        }
    };
    
    function updateBulkRequests(docList) {
        for (var row in docList) {
            updateRequest(docList[row].doc);
        }
    };

    function filterRequests() {
        var requestData = _dataByWorkflow;
        var filteredData = {}
        filteredLength = 0;
        for (var workflowName in requestData) {
            if (andFilter(requestData[workflowName], _filter)){
                filteredData[workflowName] =  requestData[workflowName];
            }
        }
        _filteredRequests.setDataByWorkflow(filteredData);
        return _filteredRequests;
    }
    
    function andFilter(base, filter) {
        var includeFlag = true;
        for (var property in filter) {
            if (base[property] !== undefined && contains(base[property], filter[property])) {
                continue;
            } else {
                includeFlag = false;
                break;
            }
        }
        return includeFlag;
    }
    
    function contains(a, b) {
        //TODO change to regular expression
        return (!b || a.toLowerCase().indexOf(b.toLowerCase()) !== -1);
    }
    function getRequestByNameAndAgent(workflow, agentUrl) {
        if (!_dataByWorkflowAgent[workflow]) {
                _dataByWorkflowAgent[workflow] = {}
        }
        
        if (!agentUrl){
            return _dataByWorkflowAgent[workflow];
        } else {
            if (!_dataByWorkflowAgent[workflow][agentUrl]){
                _dataByWorkflowAgent[workflow][agentUrl] = {};
            }
            return _dataByWorkflowAgent[workflow][agentUrl];
        }
    };
    
    function getDataByWorkflow(request, keyString, defaultVal) {
        "keyString is opject property separte by ."
        if (!request) return _dataByWorkflow;
        else if (!keyString) return _dataByWorkflow[request];
        else return _get(_dataByWorkflow[request], keyString, defaultVal);
    }
    
    function setDataByWorkflow(data) {
        "keyString is opject property separte by ."
        _dataByWorkflow = data;
    }
    
    function getList() {
        var list = [];
        for (var item in _dataByWorkflow) {
            list.push(_dataByWorkflow[item])
        }
        return list.sort(requestDateSort);
    }
    
    function requestDateSort(a, b) {
        for (var i in a.request_date) { 
            if (b.request_date[i] != a.request_date[i]) {
                return (Number(b.request_date[i]) - Number(a.request_date[i]));
            }
        }
        return 0;
    }
    
    function getWMBSJobsTotal(request) {
        var aData = _dataByWorkflow[request];
        return (_get(aData, "status.success", 0) + 
                _get(aData, "status.cooloff", 0) + 
                _get(aData, "status.canceled", 0) +
                failureTotal(request) +
                queuedTotal(request) +
                submittedTotal(request));
    }
    
    function failureTotal(request) {
        var aData = _dataByWorkflow[request];
        return (_get(aData, "status.failure.create", 0) + 
                _get(aData, "status.failure.submit", 0) + 
                _get(aData, "status.failure.exception", 0));
    };
    
    function queuedTotal(request) {
        var aData = _dataByWorkflow[request];
        return (_get(aData, "status.queued.first", 0) + 
                _get(aData, "status.queued.retry", 0));
    };
    
    function submittedTotal(request) {
        var aData = _dataByWorkflow[request];
        return (_get(aData, "status.submit.first", 0) + 
                _get(aData, "status.submit.retry", 0));
    };

    return {'getDataByWorkflow': getDataByWorkflow,
            'updateBulkRequests': updateBulkRequests,
            'updateRequest': updateRequest,
            'getList': getList,
            'getLength': getLength,
            'getWMBSJobsTotal': getWMBSJobsTotal,
            'failureTotal': failureTotal,
            'queuedTotal': queuedTotal,
            'submittedTotal': submittedTotal,
            'filterRequests': filterRequests,
            'setFilter': setFilter,
            'setDataByWorkflow': setDataByWorkflow
            }
}