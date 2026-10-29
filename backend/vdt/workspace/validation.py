"""Additive Step 06 schemas; the frozen Step 05 files are unchanged."""
from copy import deepcopy
from functools import lru_cache
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from vdt.access import validation as base


@lru_cache(maxsize=1)
def registry():
    doc = deepcopy(base.contract()[0])
    schemas = doc['components']['schemas']
    schemas['Dependency']['properties']['resource_type']['enum'] += ['branch','system','asset','data_asset']
    schemas['AssessmentScenarioLinkInput'] = {
        'type':'object','additionalProperties':False,
        'properties':{'scenario_id':{'type':'string','format':'uuid'},
                      'write_context':{'$ref':'#/components/schemas/WriteContext'}},
        'required':['scenario_id','write_context']}
    resource = Resource.from_contents(dict(doc, **{'$schema':'https://json-schema.org/draft/2020-12/schema'}))
    return Registry().with_resource('urn:vdt:workspace',resource)


@lru_cache(maxsize=32)
def validator(name):
    return Draft202012Validator({'$ref':f'urn:vdt:workspace#/components/schemas/{name}'},
                                registry=registry(),format_checker=FormatChecker())


def payload(request,name):
    return base.payload(request,name,validator=validator(name))
