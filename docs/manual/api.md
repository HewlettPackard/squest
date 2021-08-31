# REST API

## Authentication

Squest API allows tokens and session authentication.  
A token is a unique identifier mapped to a Squest user account. Each user may have one token which he or she can use for authentication when making REST API requests.
Each token contains a 160-bit key represented as 40 hexadecimal characters. Additionally, a token can be set to expire at a specific time. This can be useful if an external client needs to be granted temporary access to Squest. By default, token expires one day after its creation.  
The API token is displayed in 'Tokens' section of profile page, it can be updated by generating another one and editing.

> **Use of tokens:**
>```bash
>curl -X POST http://example.com -H "Authorization: Token YOURTOKEN"
>```
