from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
  'metadata_version': '0.1',
  'status': ['preview'],
  'supported_by': 'community'
}

class FilterModule(object):
  def filters(self):
    return {
      'tree': self.tree_builder
    }

  def tree_builder(self, value):
    tree = {}

    t = tree
    for part in value.split('.'):
        t = t.setdefault(part, {})
    return tree
