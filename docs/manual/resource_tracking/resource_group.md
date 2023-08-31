# Resource groups

In Squest, a _resource group_ is a **group of object**(resource) that are **composed by the same _Attributes_**.

_Resource groups_ can be linked to consume from each other.

## Attributes

_Attributes_ are declared in the _resource group_ as a definition of the generic object through a **tansformer**
Each resource then created in the _resource group_ may have to fill the value for each declared attribute.

### Transformer

#### Consume from another Resource Group

Each attribute of a _resource group_ can **consume** from another _attribute_ of another _resource group_ by using a **Transformer**.

E.g: The `vCPU` _attribute_ of the `VMS` _resource group_ can consume form the `CPU` attribute of the "cluster" _resource group_.

#### Factor

The factor act as an over commitment. It allows you to specify whether resources consume more or less than expected.

For example, if a host has 28 core processors and hyperthreading is enabled, that host will produce 56 vCPUs (28 cores x 2 threads
per core). This can be reflected by configuring the factor on the `vCPU` attribute to `2`.

## Tags

Tags are words that are attached to Resource Group and can then be used to filter the "Graph" representation of all Resource Group.

Tags are intended to be used to specify identifying objects that are meaningful and relevant to users. Tags can be used
to organize and select subsets of objects. Tags can be attached to objects at creation time and subsequently added and
modified at any time.

To add multiple tags:

* If the input doesn't contain any commas or double quotes, it is simply treated as a space-delimited list of tag names.

* If the input does contain either of these characters:

    * Groups of characters which appear between double quotes take precedence as multi-word tags (so double quoted tag
      names may contain commas). An unclosed double quote will be ignored.

    * Otherwise, if there are any unquoted commas in the input, it will be treated as comma-delimited. If not, it will
      be treated as space-delimited.

Examples:

| Tag input string       | Resulting tags                    | Notes                                          |
|------------------------|-----------------------------------|------------------------------------------------|
| apple ball cat         | ``["apple", "ball", "cat"]``      | No commas, so space delimited                  |
| apple, ball cat        | ``["apple", "ball cat"]``         | Comma present, so comma delimited              |
| "apple, ball" cat dog  | ``["apple, ball", "cat", "dog"]`` | All commas are quoted, so space delimited      |
| "apple, ball", cat dog | ``["apple, ball", "cat dog"]``    | Contains an unquoted comma, so comma delimited |
| apple "ball cat" dog   | ``["apple", "ball cat", "dog"]``  | No commas, so space delimited                  |
| "apple" "ball dog      | ``["apple", "ball", "dog"]``      | Unclosed double quote is ignored               |
