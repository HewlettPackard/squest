# Tools

## Global Hooks

Global hooks are a way to call a Ansible controller/AWX job template following the new state of a `Request` or an `Instance`.

For example, if you want to call a job template that performs an action everytime a `Request` switch to `FAILED` state.

Form field:

- **name:** Name of your hook
- **Model:** Target model object that will be linked to the hook (`Request` or an `Instance`)
- **State:** State of the selected `model`. The hook will be triggered when an instance of the select model type will switch to this selected state
- **Job template:** The Ansible controller/AWX job template to execute when an instance of the selected model reach the selected state
- **Extra vars:** extra variable as JSON to add to the selected job template

States documentation:

- Available states for a [`Request`](../dev/request-state-machine.md).
- Available states for a [`Instance`](../dev/instance-state-machine.md).

## Announcements

!!! note

    Configure your [time zone](/squest_settings/#time-zone).

Announcements allow Squest administrator to notify users. Announcements are displayed to end users in Dashboard page.

Administrator defines beginning, end, title, message and type of announcement.

## Custom links

Custom links allow to display arbitrary hyperlinks to external content by using Squest `instance` attributes.
Custom links appear as buttons in the top right corner of an **instance detail page**.
Jinja template can be used to insert data from the current squest `instance` details like `instance.spec`.

For example a link can be created to expose the Hypervisor URL that has been placed into the instance spec of a created resource.

| Name          | Required | Comment                                                                                     |
|---------------|----------|---------------------------------------------------------------------------------------------|
| name          | true     | Name of the custom link. When `loop` is used, the name is used for the dropdown button name |
| services      | true     | Define in which instance details page the button will appear                                |
| text          | true     | Text in the button. Jinja template supported                                                |
| url           | true     | URL of the link. Jinja template supported                                                   |
| button color  | false    | Color of the displayed button                                                               |
| when          | false    | Ansible like "when" condition                                                               |
| loop          | false    | Ansible like "loop"                                                                         |
| Enabled       | false    | Enable or disable the button                                                                |
| Is admin only | false    | When set to `true`, only Squest administrators can see the button                           |


### Jinja templating

[Jinja templating](jinja.md) can be used in the `text` or `URL` definition. The `instance` object of the current instance detail 
page is used as context.

Full `instance` object definition can be retrieved through the [API documentation](api.md).

Instance spec example:
```json
{
  "key1": "value1"
}
```

Button text example:
```
Button {{ instance.name }}
```

Button url example:
```
https://external_resource.domain/?name={{ instance.spec.key1 }}
```

Rendered button with an instance named "k8S ns test":
```html
<a href="https://external_resource.domain/?name=value1">Button k8S ns test</a>
```

### When condition

The when condition allow to display the button only on certain condition like the "when" flag on Ansible.

E.g:
```
spec['configvar'] == 'value' and user_spec['other'] == 'value'
```

!!! note

    Like for Ansible, double curly braces are not used in 'when' declaration.

### Loop

When the loop definition is set, a dropdown button is created with a link for each element of the given list.
Like for Ansible, the element is exposed as `item` in the Jinja template of the button text or URL.

Instance spec example:
```json
{
  "my_list": [
    "item1",
    "item2"
  ]
}
```

Loop example:
```
{{ instance.spec.my_list }}
```

Button text example:
```
name: {{ item }}
```

Button url example:
```
https://external_resource.domain/{{ item }}
```

Rendered links into the dropdown button:
```html
<a href="https://external_resource.domain/item1">name: item1</a>
<a href="https://external_resource.domain/item2">name: item2</a>
```
