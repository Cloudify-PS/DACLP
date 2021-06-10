#!/usr/env/bin python
from cloudify import ctx
from cloudify.state import ctx_parameters
from cloudify.exceptions import NonRecoverableError

runtime_properties = ctx_parameters['runtime_properties']
try:
    for p in runtime_properties:
        n, v = map(p.get, ['name', 'value'])
        ctx.target.instance.runtime_properties[n].remove(v)
        ctx.target.instance.runtime_properties[n] = \
            ctx.target.instance.runtime_properties[n][:]
        ctx.logger.info('source: {}'
                        .format(ctx.source.instance.runtime_properties))
        ctx.logger.info('target: {}'
                        .format(ctx.target.instance.runtime_properties))
except KeyError:
    raise NonRecoverableError('Runtime properties to fetch must be a '\
        'list of dictionaries with name and value pairs: {}'.format(runtime_properties))
