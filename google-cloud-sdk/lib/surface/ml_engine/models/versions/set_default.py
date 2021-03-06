# Copyright 2016 Google Inc. All Rights Reserved.
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
"""ml-engine models versions set-default command."""
from googlecloudsdk.calliope import base
from surface.ml_engine.versions import set_default


@base.Deprecate(
    is_removed=False,
    warning=(
        'This command is deprecated. '
        'Please use `gcloud beta ml-engine versions set-default` instead.'),
    error=('This command has been removed. '
           'Please use `gcloud beta ml-engine versions set-default` instead.'))
class SetDefaultBeta(set_default.SetDefaultBeta):
  """Sets an existing Cloud ML Engine version as the default for its model."""
  pass

