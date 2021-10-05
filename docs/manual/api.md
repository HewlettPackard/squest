# REST API

## Authentication

Squest API allows tokens and session authentication.  
The API token management is available in the **Tokens** section of your **profile** page.

A token is a unique identifier mapped to a Squest user account. Each user may have one or more tokens which can be used for 
authentication when making REST API requests.
A token can have an expiration date to grant temporary access to an external client.  

Usage example with curl
```bash
export SQUEST_TOKEN=d97ebdbeccf5fc3fba740e8e89048e3d453bd729
curl -X GET http://127.0.0.1:8000/api/resource_tracker/resource_group/ \
-H "Authorization: Bearer $SQUEST_TOKEN"
```

Usage example in Ansible URI module:
```yaml
- name: Get info from squest
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    squest_api: "http://127.0.0.1:8000/api/"
    squest_token: d97ebdbeccf5fc3fba740e8e89048e3d453bd729
    squest_bearer_token: "Bearer {{ squest_token }}"

  tasks:
    - name: Get all resource group
      uri:
        url: "{{ squest_api }}resource_tracker/resource_group/"
        headers:
          Authorization: "{{ squest_bearer_token }}"
        method: GET
        status_code: 200
        body_format: json
      register: output

    - debug:
        var: output
```

## API documentation

The API documentation is available on the URL "/swagger" of your Squest instance. 

E.g: `http://192.168.58.128/swagger/`
