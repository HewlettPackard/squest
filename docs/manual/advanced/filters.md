# JSON Accessor

In the Squest UI, certain pages offer filtering options based on JSON accessors. For instance, the instance list page allows filtering based on instance specs.

To access a field in json, simply describe the path by separating the levels by dots. The value of field to filter
must be after an equal. It is possible to make a filter on several fields which are separated by commas.

## Examples

### Instance spec with string

```json
{
  "vm_name": "vm001"
}
```

Examples of lookup string that can be used in the filter.

```
vm_name=vm001
vm_name='vm001'
vm_name="vm001"
```

### Instance spec with dict

```json
{
  "openstack": {
    "cluster_name": "cluster_perf"
  }
}
```

Example of lookup string that can be used in the filter.

```
openstack.cluster_name=cluster_perf
```

### Instance spec with list

```json
{
  "vm_disk": [
    "disk01",
    "disk02"
  ]
}
```

Example of lookup string that can be used in the filter.

```
vm_disk.0=disk01
```

### Instance spec on two fields

```json
{
  "my_first_field": {
    "my_second_field": [
      "my_value1",
      "my_value2"
    ]
  },
  "my_integer_field": 1
}
```

Example of lookup string that can be used in the filter.

```
my_first_field.my_second_field.0=my_value1,my_integer_field=1
```

### Instance spec with regex

```json
{
  "dns_name": "my_hostname.domain.example"
}
```

Lookup string example:

```
dns_name.regex=my_hostname
```
