########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.


# 'ctx' is always passed as a keyword argument to operations, so
# your operation implementation must either specify it in the arguments
# list, or accept '**kwargs'. Both are shown here.

from cloudify.decorators import workflow
from cloudify.workflows import ctx as workflow_ctx


@workflow
def call_lifecycle_operations(ctx,
                              node_instance_id,
                              operations_with_kwargs):

    ctx = workflow_ctx
    ctx.logger.info("Starting Custom Workflow")

    # update interface on the config node
    graph = ctx.graph_mode()

    # If ctx is left in the kwargs it will cause exceptions
    # It will be injected for the operation being executed anyway
    instance = ctx.get_node_instance(node_instance_id)
    sequence = graph.sequence()

    for op_with_kwargs in operations_with_kwargs:
        for op, kwargs in op_with_kwargs.items():
            # add to run operation
            sequence.add(
                instance.send_event(
                    'Starting to {} on instance {}'
                    .format(op, instance.id)),
                instance.execute_operation(op,
                                           kwargs=kwargs),
                instance.send_event('Done {}'.format(op)))

    graph.execute()
