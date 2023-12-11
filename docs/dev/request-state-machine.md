# Request state machine



```mermaid
graph TB
   
    start((Start))
    submitted[SUBMITTED]
    start --> submitted
    auto_accept{auto accept?}
    style auto_accept fill:#80CBC4
    instance_pending([instance pending])
    submitted --> instance_pending
    submitted --> |re-submit|submitted
    instance_pending --> auto_accept
    accepted[ACCEPTED]
    auto_accept -->|Yes| accepted
    admin_action_1{admin action}
    style admin_action_1 fill:#80DEEA
    auto_accept -->|No| admin_action_1
    on_hold[ON_HOLD]
    admin_action_1 -->|on_hold| on_hold
    admin_action_1 -->|cancel| canceled
    admin_action_1 -->|reject| rejected
    admin_action_1 -->|accept| accepted
    rejected[REJECTED]
    on_hold -->|reject| rejected
    canceled[CANCELED]
    on_hold --> |cancel|canceled
    on_hold --> |accept|accepted
    rejected --> |cancel|canceled
    canceled --> |delete| deleted
    deleted((Deleted))
    auto_pocess{auto process?}
    style auto_pocess fill:#80CBC4
    accepted --> auto_pocess
    accepted -->|reject| rejected
    accepted -->|review| accepted
    accepted -->|cancel| canceled
    auto_pocess --> |Yes| operation_type
    admin_action_2{admin action}
    auto_pocess --> |No| admin_action_2
    admin_action_2 --> |process| operation_type
    style admin_action_2 fill:#80DEEA
    operation_type{Operation type?}
    style operation_type fill:#80CBC4
    instance_creating([instance_creating])
    instance_updating([instance_updating])
    instance_deleting([instance_deleting])
    operation_type --> |CREATE| instance_creating
    operation_type --> |UPDATE| instance_updating
    operation_type --> |DELETE| instance_deleting
    processing[PROCESSING]   
    instance_creating --> processing
    instance_updating --> processing
    instance_deleting --> processing
    processing_ok{processing ok?}
    style processing_ok fill:#80CBC4
    processing --> processing_ok
    complete[COMPLETE] 
    failed[FAILED] 
    processing_ok --> |Yes| complete
    processing_ok --> |No| failed
    failed --> |retry| processing
    failed --> |review| accepted
    archived[ARCHIVED] 
    complete -->|archive| archived
    archived -->|unarchive| complete
```