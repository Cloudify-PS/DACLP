# DACLP

## Workflow closed-loop triggering
All workflows will be trigerred by Nagios. The commands need to be executed on
the monitored VM
### Scale out
Will add server vm instances
#### Trigger
High CPU usage
#### Command
`openssl speed`

### Scale up RAM
Changes the server size flavor
#### Trigger
Low memory
#### Command
`</dev/zero head -c 1G | tail `

### Scale up storage
Changes attached drive size
#### Trigger
Low on disk space
#### Command
`fallocate -l 20G testfile`


## VM pakcage upgrade
Allows Cloudify to trigger upgrade procedure for the VM

workflow `execute_operation`

wokrflow params
```
{
   "operation":"cloudify.interfaces.lifecycle.upgrade",
   "operation_kwargs":{

   },
   "allow_kwargs_override":true,
   "run_by_dependency_order":false,
   "type_names":[

   ],
   "node_ids":[
      "upgrade_vm"
   ],
   "node_instance_ids":[

   ]
}
```

## Confiugration update
Changes web page message

### nginx
workflow `execute_operation`

workflow params
```
{
   "operation":"cloudify.interfaces.lifecycle.update",
   "operation_kwargs":{
      "domain": "cfy-hello",
      "message": "Cloudify updated"
 
   },
   "allow_kwargs_override":true,
   "run_by_dependency_order":false,
   "type_names":[

   ],
   "node_ids":[
      "service_update"
   ],
   "node_instance_ids":[

   ]
}
```

### nodejs
workflow `execute_operation`

workflow params
```
{
   "operation":"cloudify.interfaces.lifecycle.update",
   "operation_kwargs":{
      "user": "centos",
      "message": "Cloudify updated",
      "appDir": "app"
   },
   "allow_kwargs_override":true,
   "run_by_dependency_order":false,
   "type_names":[

   ],
   "node_ids":[
      "service_update"
   ],
   "node_instance_ids":[

   ]
}
```
