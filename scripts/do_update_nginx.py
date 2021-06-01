import subprocess
from cloudify import ctx
from cloudify.state import ctx_parameters as p

path='/var/www/{}/index.html'.format(p['domain'])
p.pop('ctx', None)
ctx.download_resource_and_render('ansible/nginx/webcontent/index.j2',
                                 '/tmp/index.html',
                                 p)
returncode = subprocess.call(['/usr/bin/sudo', 'cp',  '/tmp/index.html', path])
