# Inventory usage

Please replace all variables in upercase in this directory:

In inventory replace:  
- `localhost ansible_connection=local` by your machine host where playbooks will be executed

In group_vars/squest_testing.yml replace:  
- `SQUEST_TOKEN` by a token generated in Squest by an admin 
- `SQUEST_API_URL` the URL of your Squest API (e.g. localhost:8000)