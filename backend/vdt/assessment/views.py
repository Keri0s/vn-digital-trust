"""HTTP boundary for assessment worklist."""
from vdt.access.views import boundary
from vdt.access.validation import payload
from . import service

@boundary(('GET','POST'))
def collection(request):
    return service.assessments(request) if request.method=='GET' else service.create(request,payload(request,'AssessmentInput'))

@boundary(('GET',))
def item(request,id):
    return service.assessments(request,str(id))

@boundary(('GET',))
def assignment_catalog(request):
    return service.assignment_catalog(request)

@boundary(('GET',))
def setup(request):
    return service.setup(request)

@boundary(('GET',))
def display_context(request,id=None):
    return service.assessments(request,str(id) if id else None,display_context=True)
