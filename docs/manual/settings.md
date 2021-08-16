# Settings

## Global Hooks

Global hooks are a way to call a Tower/AWX job template following the new state of a `Request` or an `Instance`.

For example, if you want to call a job template that performs an action everytime a `Request` switch to `FAILED` state.

Form field:

- **name:** Name of your hook
- **Model:** Target model object that will be linked to the hook (`Request` or an `Instance`)
- **State:** State of the selected `model`. The hook will be triggered when an instance of the select model type will switch to this selected state
- **Job template:** The Tower/AWX job template to execute when an instance of the selected model reach the selected state
- **Extra vars:** extra variable as JSON to add to the selected job template

States documentation:

- Available states for a [`Request`](../dev/request-state-machine.md).
- Available states for a [`Instance`](../dev/instance-state-machine.md).

## Announcements

> **Note: ** Configure your [time zone](/squest_settings/#time-zone).

Announcements allow Squest administrator to notify users. Announcements are displayed to end users in Dashboard page.

Administrator defines beginning, end, title, message and type of announcement.

