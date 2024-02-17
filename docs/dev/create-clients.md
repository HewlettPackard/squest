# Interact with the REST API with other languages

## golang

Step 1 - Download a swagger generator from `https://github.com/go-swagger/go-swagger`

Follow instructions from the website, you can directly use a pre-compiled version of the tool from here:  [Releases]<https://github.com/go-swagger/go-swagger/releases>

Or from the source code

Step 2 - From the swagger or opeanapi schema generates the go client source code

```pwowershell
mkdir c:\temp\squest
go mod init example.com/squest-client
go mod tidy
# squest.swagger is the openapi or swagger schema
# Get it from - https://squest.glabs.hpecorp.net/swagger/?format=openapi
swagger.exe generate client --skip-validation -A squest -f squest.swagger
```

As result you will get two directories

```console
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           2/17/2024 11:07 AM                client
d----           2/17/2024 11:07 AM                models
-a---           2/17/2024 11:05 AM             44 go.mod
```
Adjust it, move to a pkg or create your own structure

Re-excute `go mod tidy` in order to get openapi modules

```pwowershell
go mod tidy
go: finding module for package github.com/go-openapi/validate
go: finding module for package github.com/go-openapi/runtime
go: finding module for package github.com/go-openapi/strfmt
go: finding module for package github.com/go-openapi/runtime/client
go: finding module for package github.com/go-openapi/swag
go: finding module for package github.com/go-openapi/errors
go: downloading github.com/go-openapi/validate v0.23.0
go: downloading github.com/go-openapi/swag v0.22.9
go: downloading github.com/go-openapi/strfmt v0.22.0
go: downloading github.com/go-openapi/runtime v0.27.1
go: downloading github.com/go-openapi/errors v0.21.0
...
```
