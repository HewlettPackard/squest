
## Connect Squest to your controller

The first step consist into adding a **backend controller** (RHAAP/AWX).
In the left sidebar of Squest, go into the _Administration_ group, look for the **RHAAP/AWX** item and follow the steps described in the 
[administration documentation](manual/administration/rhaap.md) to add your controller.

Once added, all Job templates present on the controller should appear in Squest.

## Create your first service

Go into the _Service catalog_ --> _All Services_ and click on add a new service.

The only mandatory information here is the **name**. 

!!! note

    For more information about the other flags, refer to [service documentation](manual/service_catalog/service.md).

Once the service created, the next page invite you to create the first operation that will "create" an instance of this service.

In this form, mandatory field are a **name** and selecting the **job template** to execute in the controller.

!!! note
    
    For more information about the other flags, refer to [operation documentation](manual/service_catalog/operation.md).

## Request your service

Once the operation configured, the service is available in the catalog.
Click on the **order** button of the service to create a new _request_. 

The first page ask to give an _instance name_ which is a short name that will help you to identify and manage the lifecycle of the instance later. For example `my_test_instance`.

In the second page, Squest will ask to fill all the variable that are present in the _job template_ survey if one was attached.

The request then appears in the **Request** tab. Click on the _ID_ of the request to review it.

The request detail page gives information about the current state of the request. From here you can accept, reject, cancel or update the filled fields.

Once the request accepted, it can be processed, which means that the request is sent to the controller to execute the _Job template_.

## What next

You know the basics of Squest. You can now dig into the [service catalog](manual/service_catalog/concept.md) documentation to learn the concept of services and operations.

By default, Squest is deployed with a minimum configuration, this one can be customized by following the [settings](configuration/squest_settings.md) documentation.
