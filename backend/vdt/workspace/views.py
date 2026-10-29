from vdt.access.views import boundary
from vdt.access.validation import expected_version
from .validation import payload
from . import service


@boundary(('GET','POST','PATCH'))
def inventory(request,kind,id=None):
    if request.method=='GET': return service.collection(request,kind,id)
    if request.method=='POST' and id is None:
        return service.inventory_write(request,kind,payload(request,service.KINDS[kind][1]+'Write'))
    if request.method=='PATCH' and id is not None:
        return service.inventory_write(request,kind,payload(request,service.KINDS[kind][1]+'WritePatch'),id,expected_version(request,True))
    from vdt.access.validation import fail
    fail('METHOD_NOT_ALLOWED',405,'Phương thức không được hỗ trợ.')


@boundary(('GET','POST','PATCH'))
def scenarios(request,id=None):
    if request.method=='GET': return service.collection(request,'scenarios',id)
    if request.method=='POST' and id is None:
        return service.scenario_write(request,payload(request,'ScenarioWrite'))
    if request.method=='PATCH' and id is not None:
        return service.scenario_write(request,payload(request,'ScenarioWritePatch'),id,expected_version(request,True))
    from vdt.access.validation import fail
    fail('METHOD_NOT_ALLOWED',405,'Phương thức không được hỗ trợ.')


@boundary(('POST',))
def context_create(request): return service.create_context(request,payload(request,'ContextInput'))


@boundary(('GET',))
def snapshot(request,id,kind): return service.snapshot_read(request,kind,id)


@boundary(('POST',))
def transition(request,id):
    return service.scenario_write(request,payload(request,'ScenarioTransitionInput'),id,expected_version(request,True),transition=True)


@boundary(('POST',))
def link(request,id):
    return service.link_scenario(request,id,payload(request,'AssessmentScenarioLinkInput'),expected_version(request,True))


@boundary(('GET',))
def dossier(request,id): return service.dossier(request,id)


@boundary(('GET',))
def setup(request): return service.setup(request)
