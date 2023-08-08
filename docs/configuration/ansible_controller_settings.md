# Ansible controller configuration

Squest will need a token in order to communicate with your Ansible controller instance.

## Create an application on your Ansible controller/AWX instance

On Ansible controller, go in Application menu and create a new app with the following configuration:

- **name:** squest
- **Organization:** Default  
- **Authorization grant type:** Resource owner password based
- **Client type:** Confidential

## Create a token for Squest application

On Ansible controller/AWX:

- Go in your **Profile** page (top right corner), go into the tokens section
- Click add button
- Search for the "squest" application created previously and select it
- Give a scope "write"
- Save
- Copy the generated token. This will be the token to give to Squest when creating a new Ansible controller server instance.
