# Lifecycle management

## Populate the service catalog

Once Squest is linked to a Tower/AWX server, "services" can be added into the catalog.

A service is composed of `operations` that are pointers to "job templates" present in Tower/AWX.

A service has at least one operation of type `CREATE` that allows to provision the resource.

A service can have then multiple operation of type `UPDATE` and `DELETE` that allow to manage the lifecycle of instances that have been created via the `CREATE` operation.

## Provisioning a service

When a user request for the first time a service, an instance is created automatically and set to "pending" state on Squest.
Once approved by the administrator, the request is sent to Tower to execute the linked job template.

The executed job, aka the Ansible playbook, need to call back the Squest API in order to attach information (spec) to the pending instance.

Squest provisioning workflow:
```mermaid
sequenceDiagram
    participant User
    participant Admin
    participant Squest
    participant Tower
    User->>Squest: Request service
    Admin->>Squest: Approve
    Admin->>Squest: Process
    Squest->>Tower: Process
    Squest-->>Tower: Check
    Note right of Tower: Running
    Tower->>Squest: Instance spec <br> {'uuid': 34, 'name': 'instance_name'}
    Squest-->>Tower: Check
    Note right of Tower: Successful    
    Squest->>User: Notify service ready
```

The playbook will receive a `squest` extra variable that contains information of to the pending instance linked to the request
in addition to all extra variables which come from the survey of the job template.

Example of extra variables sent by Squest:
```yaml
squest:
  squest_host: http://squest.domain.local
  request:
    instance:
      id: 1
      name: test
      service: 1
      spec:
        file_name: foo.conf
      state: PROVISIONING
      spoc: 2
```

Specs related to the created instance are important in order to be sent later to a playbook in charge of updating
this particular instance.

Sent specs must contain unique IDs that allow to identify precisely the instance.
(E.g: `uuid` of a VMware VM, `namespace` and `cluster_api_url` for an Openshift project)


### Playbook example

In the example below, we've configured a job template with a survey that ask for a variable named `file_name`.
The playbook will:

- create the resource (the file)
- call Squest api to link spec of the created resource to the instance

```yaml
- name: Create a file
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    squest_token: 48c67f9c2429f2d3a1ee0e47daa00ffeef4fe744
    squest_bearer_token: "Bearer {{ squest_token }}"
    squest_api_url: "http://192.168.58.128:8000/api/"

  tasks:
    - name: Print the job template survey variable
      debug:
        var: file_name

    - name: Print info sent by Squest
      debug:
        var: squest

    - name: Create a file with the given file_name
      ansible.builtin.file:
        path: "/tmp/{{ file_name }}"
        owner: user
        group: user
        mode: '0644'
        state: touch

    - name: Update spec of the instance via the squest API
      uri:
        url: "{{ squest_api_url }}service_catalog/instance/{{ squest['request']['instance']['id'] }}/" # do not forget the last slash
        headers:
          Authorization: "{{ squest_bearer_token }}"
        method: PATCH
        body:
          spec:
            file_name: "{{ file_name }}"
        status_code: 200
        body_format: json
```

## Day 2 operations

Day 2 operations are operations that **update** or **delete** existing resources.

!!! note

    By default, recent version of AWX/Tower drop extra variables that are not declared in the survey. To be able to receive Squest extra vars you need to enable "Prompt on Launch" in the "Variables" section of you job template. This correspond to the flag "ask_variables_on_launch" of the job_template model on the Tower/AWX API.

When a user creates a request for a day 2 operation of a provisioned instance, Squest automatically attach an `extra_vars` named `squest`
that contains the instance spec sent by the playbook used to provision at first the resource.

The playbook used to update the instance need to use info placed in `squest` variable to retrieve the real resource that need to be updated or deleted.
The update playbook can send a new version of the instance to squest at the end of its process if required.

```mermaid
sequenceDiagram
    participant User
    participant Admin
    participant Squest
    participant Tower
    User->>Squest: Request update
    Admin->>Squest: Approve
    Admin->>Squest: Process
    Squest->>Tower: Process - Extra vars:<br> {'squest': {'uuid': 34, 'name': 'instance_name'}}
    Squest-->>Tower: Check
    Note right of Tower: Running
    Tower->>Squest: Instance spec update <br> {'uuid': 34, 'name': 'instance_new_name}
    Squest-->>Tower: Check
    Note right of Tower: Successful    
    Squest->>User: Notify service updated
```

### Playbook example

Example of extra vars sent by squest:
```yaml
squest:
  squest_host: http://squest.domain.local
  request:
    instance:
      id: 1
      name: test-instance
      service: 1
      spec:
        file_name: foo.conf
      spoc: 2
      state: UPDATING
string_to_place_in_file: "this is a string"
```

In the example below, the update job template survey ask for a `string_to_place_in_file` variable.
The playbook receive as well all information that help to retrieve the resource to update. In this example the resource is the `file_name`.
```yaml
- name: Update content of a file
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: Print the job template survey variable
      debug:
        var: string_to_place_in_file

    - name: Print info sent by Squest
      debug:
        var: squest

    - name: Add content into the file_name given by squest instance spec
      ansible.builtin.lineinfile :
        path: "/tmp/{{ squest['request']['instance']['spec']['file_name'] }}"
        line: "{{ string_to_place_in_file }}"
        create: yes
```

## Operation survey

The survey of an operation can be edited to change the behavior of the generated form of a request.

!!! note

    Surveys in Squest are actually surveys attached to each job templates in your Tower/AWX.
    Squest can only disable the ones that you don't want to be filled by your end users.
    Those fields, if declared as mandatory on Tower/AWX, will need to be filled anyway by the admin when approving a request.

### Enabled fields

An **enabled** field is displayed into the end user survey.
By default, all fields are enabled when creating a new operation.

!!! note

    If the field is set as **required** into the Tower/AWX job template survey config then the administrator
    will have to fill it in any case during the review of the request.

### Default value


When set, the default value is pre-filled into the final form. It takes precedence over the default value set in Tower/AWX job template survey config.

Default value precedence: 

 1. Default from Tower/AWX
 2. Default from Squest value
 3. User's input
 4. Admin's input

!!! note

    When used with a 'multiple select' or 'multiple select multiple' type of field, the value need to be a valid one from the Tower/AWX survey field options.

#### Hard coded string

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": "linux"
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Default config</strong></td>
        <td>My hard coded value</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td> My hard coded value </td>
    </tr>
</table>

#### With spec variable

Jinja templating can be used to load a value with the content of the instance spec or user spec.
Use variables `spec` and/or `user_spec` like with Ansible.

!!! note

    The `spec` and `user_spec` variables are only usable on **Update** or **Delete** operations as the pending instance does not contain any spec before its provisioning.

!!! note

    If the given variable key doesn't exist, the default value will be set to an empty string.

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": "linux"
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Default config</strong></td>
        <td> {{ spec.os }} </td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>linux</td>
    </tr>
</table>

#### String and spec variable

Like with Ansible, a string can be concatenated to a spec variable.

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": "linux"
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Default config</strong></td>
        <td>My hard coded value with {{ spec.os }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>My hard coded value with linux</td>
    </tr>
</table>

#### Spec dict access

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": {
                        "linux": "ubuntu"
                    }
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Default config</strong></td>
        <td>{{ spec.os['linux'] }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>ubuntu</td>
    </tr>
</table>

#### Spec list access

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": ["linux", "windows"]
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Default config</strong></td>
        <td>{{ spec.os[1] }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>windows</td>
    </tr>
</table>

#### Jinja filters

Jinja filters can also be used to transform spec variables.

For example, the 'multiple select multiple' field type requires a list of string separated with a carriage return marker (`\n`).

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": ["linux", "windows"]
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Default config</strong></td>
        <td>{{ spec.os | join('\n') }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>linux\nwindows</td>
    </tr>
</table>

## External support URL

Squest has an integrated support management. End user can open a support ticket on available instances.
An external url can be defined as support tool in each service configuration. This allows to configure for example a redirection to services like GitHub issues or Jira. 

The external support URL support jinja templating to insert the current instance metadata as query parameters.

E.g: 
```
http://my_external_tool.domain.local/?instance_name={{ instance.name }}?instance_id={{ instance.id }}?vm_os={{ instance.spec.vm_os }}
```

Example with [Github issue query parameters](https://docs.github.com/en/enterprise-server@3.1/issues/tracking-your-work-with-issues/creating-an-issue#creating-an-issue-from-a-url-query):
```
https://github.com/HewlettPackard/squest/issues/new?title=Templated+Github+issue&body=Instance%3A+{{ instance.name }}
```

!!! note

    Special characters need to be converted into a format that can be transmitted over the Internet. URLs can only be sent over the Internet using the ASCII character-set.
