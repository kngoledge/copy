# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Compute resource transforms and symbols dict.

A resource transform function converts a JSON-serializable resource to a string
value. This module contains built-in transform functions that may be used in
resource projection and filter expressions.

NOTICE: Each TransformFoo() method is the implementation of a foo() transform
function. Even though the implementation here is in Python the usage in resource
projection and filter expressions is language agnostic. This affects the
Pythonicness of the Transform*() methods:
  (1) The docstrings are used to generate external user documentation.
  (2) The method prototypes are included in the documentation. In particular the
      prototype formal parameter names are stylized for the documentation.
  (3) The 'r', 'kwargs', and 'projection' args are not included in the external
      documentation. Docstring descriptions, other than the Args: line for the
      arg itself, should not mention these args. Assume the reader knows the
      specific item the transform is being applied to. When in doubt refer to
      the output of $ gcloud topic projections.
  (4) The types of some args, like r, are not fixed until runtime. Other args
      may have either a base type value or string representation of that type.
      It is up to the transform implementation to silently do the string=>type
      conversions. That's why you may see e.g. int(arg) in some of the methods.
  (5) Unless it is documented to do so, a transform function must not raise any
      exceptions related to the resource r. The `undefined' arg is used to
      handle all unusual conditions, including ones that would raise exceptions.
      Exceptions for arguments explicitly under the caller's control are OK.
"""

import httplib
from googlecloudsdk.api_lib.compute import constants
from googlecloudsdk.api_lib.compute import instance_utils
from googlecloudsdk.core.resource import resource_transform


def TransformFirewallRule(r, undefined=''):
  """Returns a compact string describing a firewall rule.

  The compact string is a comma-separated list of PROTOCOL:PORT_RANGE items.
  If a particular protocol has no port ranges then only the protocol is listed.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    A compact string describing the firewall rule in r.
  """
  protocol = r.get('IPProtocol', None)
  if protocol is None:
    return undefined
  rule = []
  port_ranges = r.get('ports', None)
  if port_ranges is None:
    rule.append(protocol)
  else:
    for port_range in port_ranges:
      rule.append('{0}:{1}'.format(protocol, port_range))
  return ','.join(rule)


def TransformImageAlias(r, undefined=''):
  """Returns a comma-separated list of alias names for an image.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    A comma-separated list of alias names for the image in r.
  """
  name = r.get('name', None)
  if name is None:
    return undefined
  project = resource_transform.TransformScope(
      r.get('selfLink', ''), 'projects').split('/')[0]
  aliases = [alias for alias, value in constants.IMAGE_ALIASES.items()
             if name.startswith(value.name_prefix)
             and value.project == project]
  return ','.join(aliases)


def TransformLocation(r, undefined=''):
  """Return the region or zone name.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    The region or zone name.
  """
  for scope in ('zone', 'region'):
    if scope in r:
      return resource_transform.TransformBaseName(r[scope], undefined)
  return undefined


def TransformLocationScope(r, undefined=''):
  """Return the location scope name, either region or zone.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    The location scope name, either region or zone.
  """
  for scope in ('zone', 'region'):
    if scope in r:
      return scope
  return undefined


def TransformMachineType(r):
  """Return the formatted name for a machine type.

  Args:
    r: JSON-serializable object.

  Returns:
    The formatted name for a machine type.
  """
  if not isinstance(r, basestring):
    return r
  custom_cpu, custom_ram = instance_utils.GetCpuRamFromCustomName(r)
  if not custom_cpu or not custom_ram:
    return r
  # Restricting output to 2 decimal places
  custom_ram_gb = '{0:.2f}'.format(float(custom_ram) / (2 ** 10))
  return 'custom ({0} vCPU, {1} GiB)'.format(custom_cpu, custom_ram_gb)


def TransformNextMaintenance(r, undefined=''):
  """Returns the timestamps of the next scheduled maintenance.

  All timestamps are assumed to be ISO strings in the same timezone.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    The timestamps of the next scheduled maintenance or undefined.
  """
  if not r:
    return undefined
  next_event = min(r, key=lambda x: x.get('beginTime', None))
  if next_event is None:
    return undefined
  begin_time = next_event.get('beginTime', None)
  if begin_time is None:
    return undefined
  end_time = next_event.get('endTime', None)
  if end_time is None:
    return undefined
  return '{0}--{1}'.format(begin_time, end_time)


def TransformOperationHttpStatus(r, undefined=''):
  """Returns the HTTP response code of an operation.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if there is no response code.

  Returns:
    The HTTP response code of the operation in r.
  """
  if isinstance(r, dict) and r.get('status', None) == 'DONE':
    return r.get('httpErrorStatusCode', None) or httplib.OK
  return undefined


def TransformProject(r, undefined=''):
  """Returns a project name from a selfLink.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    A project name for selfLink from r.
  """
  project = resource_transform.TransformScope(
      resource_transform.GetKeyValue(r, 'selfLink', ''),
      'projects').split('/')[0]
  return project or undefined


def TransformQuota(r, undefined=''):
  """Formats a quota as usage/limit.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    The quota in r as usage/limit.
  """
  if not r:
    return undefined
  usage = r.get('usage', None)
  if usage is None:
    return undefined
  limit = r.get('limit', None)
  if limit is None:
    return undefined
  try:
    if usage == int(usage) and limit == int(limit):
      return '{0}/{1}'.format(int(usage), int(limit))
    return '{0:.2f}/{1:.2f}'.format(usage, limit)
  except (TypeError, ValueError):
    return undefined


def TransformStatus(r, undefined=''):
  """Returns the machine status with deprecation information if applicable.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    The machine status in r with deprecation information if applicable.
  """
  status = r.get('status', None)
  deprecated = r.get('deprecated', '')
  if deprecated:
    return '{0} ({1})'.format(status, deprecated.get('state', ''))
  return status or undefined


def TransformZone(r, undefined=''):
  """Returns a zone name from a selfLink.

  Args:
    r: JSON-serializable object.
    undefined: Returns this value if the resource cannot be formatted.

  Returns:
    A zone name for selfLink from r.
  """
  project = resource_transform.TransformScope(
      resource_transform.GetKeyValue(r, 'selfLink', ''), 'zones').split('/')[0]
  return project or undefined


_TRANSFORMS = {

    'firewall_rule': TransformFirewallRule,
    'image_alias': TransformImageAlias,
    'location': TransformLocation,
    'location_scope': TransformLocationScope,
    'machine_type': TransformMachineType,
    'next_maintenance': TransformNextMaintenance,
    'operation_http_status': TransformOperationHttpStatus,
    'project': TransformProject,
    'quota': TransformQuota,
    'status': TransformStatus,
    'zone': TransformZone,
}


def GetTransforms():
  """Returns the compute specific resource transform symbol table."""
  return _TRANSFORMS
