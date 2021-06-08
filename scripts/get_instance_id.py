from cloudify import ctx


ctx.instance.runtime_properties['instance_id'] = ctx.instance.id
