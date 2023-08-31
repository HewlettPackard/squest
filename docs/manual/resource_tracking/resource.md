# Resources

A _Resource_ is an instance of a _Resource Group_.
One or more resource can be linked to the Service catalog "instances".

## Link a service catalog instance

Resources can be created from the API. It allows to create automatically a new resource in a resource group when 
something is provisioned from the service catalog.

In the example below, the playbook executed in RHAAP/AWX would have created a VM. 
At the end of the process we call the squest API to instantiate a resource in the right resource group to reflect the 
consumption.
We link as well the pending instance(given by `squest.instance.id`) to this resource via the flag `service_catalog_instance`.
```yaml
- name: Add resource in resource group example
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    squest_token: xxxxxxxxxxxxxx
    squest_bearer_token: "Bearer {{ squest_token }}"
    squest_api: "http://127.0.0.1:8000/api/"
    resource_group_vm_id: 8
    squest: # this would be the data sent from squest as extra vars
      instance:
        id: 8
        name: test
        service: 1
        spec: { }
        state: PROVISIONING
    vm_name: "test-vm"
    vm_vcpu: 4
    vm_memory: 16
    desc: "My description"

  tasks:
    - name: Print info sent by Squest
      debug:
        var: squest

    # -----------------------
    # PLACE HERE ALL THE MAGIC TO CREATE THE RESOURCE
    # -----------------------
    - name: Create a resource in squest
      uri:
        url: "{{ squest_api }}resource_tracker/resource/"
        headers:
          Authorization: "{{ squest_bearer_token }}"
        method: POST
        status_code: 201
        body_format: json
        body:
          name: "{{ vm_name }}"
          resource_group: "{{ resource_group_vm_id }}"
          service_catalog_instance: "{{ squest['instance']['id'] }}"
          resource_attributes:
            - name: "vCPU"
              value: "{{ vm_vcpu }}"
            - name: "Memory"
              value: "{{ vm_memory }}"
```
