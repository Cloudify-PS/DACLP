# DACLP
DHL Automated Closed-Loop Proof of Concept is about orchestrating of both environment & application within Azure cloud with advance day 2 operations and full load balancing management.  
The main blueprint `blueprint.yaml` consists of 3 modules (service components) which are:
- Nagios monitoring - creating VM and all necessary networking resources for Nagios and installing Nagios software on top of that
- F5 BIGIP Load Balancer - deploying all resources nedded to run F5 BigIP software, installing and configuring load balancing service
- Virtual Machine running a hello-world application in Azure public cloud

## Inputs
The main blueprint takes inputs which are then propagated to a relevant deployment created by service-component.
- `app_server_type` - server type that the application will be hosted on. Should be `NGINX` or `NodeJS`
- `target_resource_tenant` - name of the Cloudify tenant which should be used to deploy resources. Should be `Test`, `Dev` or `Prod`.
- `location` - Azure Region to create resources within. Default value is `westeurope`.
- `resource_group` - name of the pre-created resource group which will contain all created resources. Default value is `dhl-poc-rg`.
- `webserver_vm_size` - name of the Virtual Machine size in Azure. Default value is `Standard_A1_v2`.
- `webserver_vm_image` - description of the Virtual Machine image in Azure. For the purpose of the POC demo it should be a Ubuntu 18.04-LTS image.
- `webserver_vm_os_family` - name of the OS family. In this case it should be `linux`.
- `webserver_vm_os_username` - name of the user to be created on a newly spun-up virtual machine with web application.
- `cpu_idle_threshold` - idle percentage of cpu usage on Application VM to trigger scale-out by Nagios. Default value is `20`.
- `used_storage_percentage_threshold` - percentage of used storage on Application VM to trigger storage scale-up by Nagios. Default value is `50`.

## Prerequisites
In order to successfully install the whole deployment there should be:
- Resource group (for example `dhl-poc-rg`) existing in the Azure environment.  
The resource group should contain a default network named <resource_group_name>-vnet (e.g. `dhl-poc-rg-vnet`) with three subnets:
   - `mgmt_subnet`
   - `wan_subnet`
   - `default`

   Cloudify Manager should be connected to both `mgmt_subnet` and `default` subnets.
- Following plugins installed on the Cloudify Manager:
   - [cloudify-utilities-plugin](https://github.com/cloudify-incubator/cloudify-utilities-plugin/releases/tag/latest)
   - [cloudify-azure-plugin](https://github.com/cloudify-cosmo/cloudify-azure-plugin/releases/tag/latest)
   - [cloudify-managed-nagios-plugin](https://github.com/cloudify-cosmo/cloudify-managed-nagios-plugin/releases/tag/latest)
   - [cloudify-nagiosrest-plugin](https://github.com/cloudify-cosmo/cloudify-nagiosrest-plugin/releases/tag/latest)
   - [cloudify-ansible-plugin](https://github.com/cloudify-cosmo/cloudify-ansible-plugin/releases/tag/latest)
   - [cloudify-daclp-plugin](https://github.com/Cloudify-PS/DACLP/tree/day3_dev/plugin)
- Following secrets defined in the secrets store in Cloudify Manager:
   - `cloudify_manager_user_name` - name of the Cloudify Manager user.
   - `cloudify_manager_user_password` - password of the Cloudify Manager user.
   - `azure_client_id` - the account subscription ID.
   - `azure_client_secret` - the Service Principal tenant.
   - `azure_subscription_id` - the Service Principal appId.
   - `azure_tenant_id` - the Service Principal password.
   - `nagios_user` - name for Nagios user.
   - `nagios_password` - password for Nagios user.
   - `snmp_user` - name for SNMP user.
   - `snmp_pass` - password for SNMP user.
   - `bigip_username` - name for F5 BIGIP user.
   - `bigip_password` - password for F5 BIGIP user.
   - `bigip_license` - license key for the F5 BIGIP software. Should be in XXXXX-XXXXX-XXXXX-XXXXX-XXXXXXX format.
   - `nodejs_index_user` - centos
   - `nodejs_app_dir` - app
   - `nginx_domain` - cfy-hello

## DACLP architecture
The purpose of this demo was to deploy a whole network infrastructure with VMs running a hello-world web-application using NGINX or NodeJS server in Azure environment, monitoring VM instances with Nagios software and using F5 BIGIP Load Balancer.

### Nagios
The setup deploys an Azure VM (Centos 7.9) with all required networking resources and installs Nagios software on top of it.  
Nagios is initially configured and prepared to perform following checks on application VMs:
- reachability check - ICMP check, pinging to check instance health.
- CPU load check - gets cpu idle percentage
- storage check - gets disk usage percentage
- ram check - gets sum of used ram

### F5 BIGIP Load Balancer
F5 BIGIP deployment uses already created subnets (`mgmt_subnet`, `wan_subnet`, `default`) from the virtual network of provided resource group.  
It creates all necessary networking resources as long as the Azure `f5-big-all-1slot-byol` virtual machine which runs F5 BIGIP software.  
Once the VM is spun-up, Cloudify performs an initial configuration of VLANs and installs the license of the key provided from the input.  

### Azure Vm with application
This deployment is split into two parts: `blueprint-azure-nginx` and `blueprint-azure-nodejs`. Both of them use `blueprint-common` as a common part with all necessary networking resources and virtual machine creation.  
After the virtual machine is successfully created, Cloudify installs the application on NGINX or NodeJS server using Ansible plugin, connects the VM to the Nagios monitoring and configures F5 BIGIP Load Balancer to properly balance the traffic.  
All needed resources are contained in scaling group so there is a possibility to scale the backend of the application.

### Architecture diagram
![Alt text](img/dhl-poc-diagram.png?raw=true "DACLP diagram")

### Jenkins
Additionally, creating the main deployment and all the resources can be achieved using Jenkins.  
In order to do that, there should be another VM manually created with Jenkins installed on top of it. After configuring the build workflow, Jenkins can trigger installation and uninstallation of the deployment.

![Alt text](img/dhl-poc-jenkins-diagram.png?raw=true "DACLP with Jenkins diagram")

### Saved files
- [Cloudify Manager snapshot](https://drive.google.com/file/d/1ZWjTk3yEdJ3WzrJnVKSKODoQnCar0fE_/view?usp=sharing)
- [Jenkins machine files](https://drive.google.com/file/d/1lwzXSm6nNDAUWnAerK7YWrEghKwdRC2o/view?usp=sharing)

## Workflow closed-loop triggering
All workflows will be trigerred by Nagios. It performes checks periodically and in case some threshold is exceeded, Nagios triggers relevant workflow on the deployment. The commands need to be executed on the monitored VM.

### Heal
When the VM is not reachable using ICMP ping, Nagios triggers the heal workflow.
It stops and deletes the VM and creates a new one with the same parameters, IP address and storage.
#### Trigger
Vm not reachable
#### Command
`sudo iptables -A INPUT -p icmp --icmp-type echo-request -j REJECT`

### Scale out
When the CPU usage on the monitored VM will be higher than defined treshold, Nagios triggers scale-out workflow.
It will add server VM instances as new instances of backend VMs, connect that VM to monitoring and add it to the F5 Load Balancer configuration.
#### Trigger
High CPU usage
#### Command
`openssl speed`

### Scale up RAM
When the free RAM memory is below defined level, Nagios triggers scale-up workflow which adds more vCPUs and RAM memory to the machine.  
VM is stopped for a moment, the server size flavor is changed and VM is started once again.
#### Trigger
Low RAM memory
#### Command
`</dev/zero head -c 1G | tail `

### Scale up storage
When the disk usage level is too high, Nagios triggers scale-up workflow which adds more storage to the VM. It changes the size of the drive attached to VM.
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

# Testing
## Setup env variables
Adjust only the first line
```
export DEPLOYMENT_VERSION=${USER}_`date --iso-8601=seconds | tr -d '+:'` && \
export DAY3_BLUEPRINT_ID=${DEPLOYMENT_VERSION}_day3 && \
export NAGIOS_BLUEPRINT_ID=${DEPLOYMENT_VERSION}_nagios && \
export NGINX_BLUEPRINT_ID=${DEPLOYMENT_VERSION}_nginx && \
export NODEJS_BLUEPRINT_ID=${DEPLOYMENT_VERSION}_nodejs && \
export BIGIP_BLUEPRINT_ID=${DEPLOYMENT_VERSION}_bigip
```

## Deploy
```
cfy blueprints upload -b ${NAGIOS_BLUEPRINT_ID} blueprint-nagios.yaml && \
cfy blueprints upload -b ${NGINX_BLUEPRINT_ID} blueprint-azure-nginx.yaml && \
cfy blueprints upload -b ${NODEJS_BLUEPRINT_ID} blueprint-azure-nodejs.yaml && \
cfy blueprints upload -b ${BIGIP_BLUEPRINT_ID} blueprint-f5-bigip.yaml && \
cfy install -i deployment_version=${DEPLOYMENT_VERSION} -b ${DAY3_BLUEPRINT_ID} -d ${DAY3_BLUEPRINT_ID} blueprint-day3.yaml
```

## Remove
The command below will run in background 
```
nohup sh -c "cfy uninstall -p ignore_failure=true ${DAY3_BLUEPRINT_ID} || \
cfy blueprints delete ${DAY3_BLUEPRINT_ID} ; \
cfy blueprints delete ${NAGIOS_BLUEPRINT_ID} ; \
cfy blueprints delete ${NGINX_BLUEPRINT_ID} ; \
cfy blueprints delete ${BIGIP_BLUEPRINT_ID} ; \
cfy blueprints delete ${NODEJS_BLUEPRINT_ID} " &
```
