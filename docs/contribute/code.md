# Contributing: code

The community can contribute to Squest by providing some new features, bug fix and enhancements.

**How to contribute**

1. Fork it!
1. Checkout the dev branch `git checkout dev`
1. Create your feature branch: `git checkout -b my-new-feature`
1. Commit your changes: `git commit -am 'Add some feature'`
1. Push to the branch: `git push origin my-new-feature`
1. Submit a pull request in the **dev** branch

If you are new on Github environment, we recommend you to read the [first contribution guide](https://github.com/firstcontributions/first-contributions).

Follow the [development environment setup documentation](../dev/dev-env.md) to prepare your workstation with prerequisites.

## Constraints

Respect [PEP 257](https://www.python.org/dev/peps/pep-0257/) -- Docstring conventions. 
For each class or method add a description with summary, input parameter, returned parameter,  type of parameter
    
```python
def my_method(my_parameter):
    """
    Description of he method
    :param my_parameter: description of he parameter
    :type my_parameter: str
    """
    pass
```

Respect [PEP 8](https://www.python.org/dev/peps/pep-0008/) -- Style Guide for Python Code
We recommend the usage of an IDE like [Pycharm](https://www.jetbrains.com/pycharm/)
