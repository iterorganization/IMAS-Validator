Rule Filtering
==============

Users can filter which subset of the found validation rules should be applied.
This is done through the options:
- name
- ids
The filter returns only the rules that adhere to all these conditions:

Code examples
-------------

Below are some examples:

To get all rules with 'time' in their name
.. code-block:: python

  rule_filter = RuleFilter(name = ['time'])

To get all rules concerning 'core_profile' idss
.. code-block:: python

  rule_filter = RuleFilter(ids = ['core_profile'])

To get all rules with both 'core' and 'density' in their name
.. code-block:: python

  rule_filter = RuleFilter(name = ['core', 'density'])

To get all rules with 'temperature' in their name concerning 'equilibrium' idss
.. code-block:: python

  rule_filter = RuleFilter(name = ['temperature'], ids = ['equilibrium'])

CLI examples
------------

TBA