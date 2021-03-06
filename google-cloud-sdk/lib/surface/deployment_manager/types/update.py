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

"""types update command."""

from googlecloudsdk.api_lib.deployment_manager import dm_labels
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.deployment_manager import composite_types
from googlecloudsdk.command_lib.deployment_manager import dm_beta_base
from googlecloudsdk.command_lib.deployment_manager import dm_write
from googlecloudsdk.command_lib.deployment_manager import flags
from googlecloudsdk.command_lib.util import labels_util
from googlecloudsdk.core import log


def LogResource(request, async):
  log.UpdatedResource(request.compositeType,
                      kind='composite_type',
                      async=async)


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA)
class Update(base.UpdateCommand):
  """Update a composite type."""

  detailed_help = {
      'EXAMPLES': """\
          To update a composite type, run:

            $ {command} my-composite-type --status EXPERIMENTAL --description "My type."
          """,
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    flags.AddAsyncFlag(parser)
    composite_types.AddCompositeTypeNameFlag(parser)
    composite_types.AddDescriptionFlag(parser)
    composite_types.AddStatusFlag(parser)
    labels_util.AddUpdateLabelsFlags(parser)

  def Run(self, args):
    """Run 'types update'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Raises:
      HttpException: An http error response was received while executing api
          request.
    """
    messages = dm_beta_base.GetMessages()
    composite_type_ref = composite_types.GetReference(args.name)
    get_request = messages.DeploymentmanagerCompositeTypesGetRequest(
        project=composite_type_ref.project,
        compositeType=args.name)
    existing_ct = dm_beta_base.GetClient().compositeTypes.Get(get_request)

    labels = dm_labels.UpdateLabels(
        existing_ct.labels,
        messages.CompositeTypeLabelEntry,
        labels_util.GetUpdateLabelsDictFromArgs(args),
        labels_util.GetRemoveLabelsListFromArgs(args))

    composite_type = messages.CompositeType(
        name=args.name,
        description=args.description,
        status=args.status,
        templateContents=existing_ct.templateContents,
        labels=labels)

    update_request = messages.DeploymentmanagerCompositeTypesUpdateRequest(
        project=composite_type_ref.project,
        compositeType=args.name,
        compositeTypeResource=composite_type)

    dm_write.Execute(update_request,
                     args.async,
                     dm_beta_base.GetClient().compositeTypes.Update,
                     LogResource)

