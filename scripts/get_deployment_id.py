from cloudify import ctx
ctx.instance.runtime_properties['deployment_id'] = ctx.deployment.id
