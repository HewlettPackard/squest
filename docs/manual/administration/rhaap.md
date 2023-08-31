# RHAAP/AWX

Squest need to be connected to a RHAAP (Red Hat Ansible Automation Platform) or AWX controller in order to work.

Operations in Squest services are actually pointers to job templates in those controllers.

Squest will need a token in order to communicate to the API of your RHAAP/AWX instance.

## RHAAP/AWX configuration

**Create an application:**

On RHAAP/AWX, go in Application menu and create a new app with the following configuration:

- **name:** squest
- **Organization:** Default  
- **Authorization grant type:** Resource owner password based
- **Client type:** Confidential

**Create a token:** 

- Go in your **Profile** page (top right corner), go into the tokens section
- Click add button
- Search for the "squest" application created previously and select it
- Give a scope "write"
- Save and copy the generated token. This will be the token to give to Squest when creating a new RHAAP/AWX server instance.

## Add a controller in Squest

Configuration:

| Name       | Description                                                                             |
|------------|-----------------------------------------------------------------------------------------|
| Name       | Short name of the RHAAP/AWX controller                                                  |
| Host       | FQDN of the server to connect with the port (no protocol). `E.g: awx.mydomain.net:8043` |
| Token      | Token created from the previous section                                                 |
| Is secure  | Enable this flag if the protocol is HTTPS (by default)                                  |
| SSL verify | Enable this flag to check the server certificate                                        |
| Extra vars | Add extra vars in json format that will be sent on every job of this controller         |
