# Approval

By default, _Requests_ can be approved by any administrator when
_Approval Workflow_ is not defined in the _Operation_. After being approved, the _Request_ is in 'ACCEPTED' state and can be
processed.

## Approval Workflow

An _Approval Workflow_ is composed by one or multiple [_Approval Step_](#approval-step).
_Approval Steps_ of the Workflow must be approved one by one following the order. After accepting the last one, the
request witch to 'ACCEPTED' state and can be processed.

!!! note

      The auto-accept option can not be set in the _Operation_ with an Approval Workflow.

## Approval Step

An _Approval Step_ can only be approved by its _Teams_ members. It is approved when all _Teams_ approved the _Request_ or at
least one depending on the [Type](#type).

!!! note

      Approval Steps are linked to Teams and not users. It means that any member can approved for his Team.

| Name  | Description                                                            |
|-------|------------------------------------------------------------------------|
| Name  | Unique identifier of the _Approval Step_ in the _Approval Workflow_.   |
| Type  | Defined how the _Approval Step_ is Approved. See supported types below |
| Teams | List of Teams that can approve the Approval Step.                      |


### Type

- **At least one:** At least one team must approve the _Approval Step_ to move to the next one.
- **All of them:** All teams of the _Approval Step_ must approve to move to the next one.
