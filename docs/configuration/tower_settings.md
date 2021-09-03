# Tower configuration

Squest will need a token in order to communicate with your Tower instance.

## Create an application on your Tower/AWX instance

On Tower, go in Application menu and create a new app with the following configuration:

- **name:** squest
- **Organization:** Default  
- **Authorization grant type:** Resource owner password based
- **Client type:** Confidential

## Create a token for Squest application

On Tower/AWX:

- Go in your **User Details** page (top right corner), go into the tokens section
- Click add button
- Search for the "squest" application created previously and select it
- Give a scope "write"
- Save
- Copy the generated token. This will be the token to give to Squest when creating a new Tower server instance.
