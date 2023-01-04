# JSON Accessor

To access a field in json, simply describe the path by separating the levels by dots. The value of field to filter
must be after an equal. It is possible to make a filter on several fields which are separated by commas.

## Examples

### Instance spec with string

```json
{
  "my_first_field": "my_value"
}
```

Examples of lookup string that can be used in the filter.

```
my_first_field=my_value
my_first_field='my_value'
my_first_field="my_value"
```

### Instance spec with dict

```json
{
  "my_first_field": {
    "my_second_field": "my_value"
  }
}
```

Example of lookup string that can be used in the filter.

```
my_first_field.my_second_field=my_value
```

### Instance spec with list

```json
{
  "my_first_field": [
    "my_value1",
    "my_value2"
  ]
}
```

Example of lookup string that can be used in the filter.

```
my_first_field.0=my_value1
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
