import subprocess
from cloudify import ctx
from cloudify.state import ctx_parameters as p

path='/home/{}/{}/index.html'.format(p['user'], p['appDir'])
p.pop('ctx', None)
ctx.download_resource_and_render('ansible/nodejs/templates/index.j2',
                                 '/tmp/index.html',
                                 p)

returncode = subprocess.call(['/usr/bin/sudo', 'cp',  '/tmp/index.html', path])
