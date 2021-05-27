#!/usr/env/bin python
from cloudify import ctx
from cloudify.state import ctx_parameters
from cloudify.exceptions import NonRecoverableError

runtime_properties = ctx_parameters['runtime_properties']
try:
    for p in runtime_properties:
        n,v = map(p.get, ['name','value'])
        ctx.source.instance.runtime_properties[n] = v
except KeyError:
    raise NonRecoverableError('Runtime properties to fetch must be a '\
        'list of dictionaries with name and value paris')
