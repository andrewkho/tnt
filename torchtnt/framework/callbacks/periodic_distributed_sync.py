# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging

from torchtnt.framework.callback import Callback
from torchtnt.framework.state import State
from torchtnt.framework.unit import TPredictUnit
from torchtnt.utils.distributed import barrier

logger: logging.Logger = logging.getLogger(__name__)


class PeriodicDistributedSync(Callback):
    """
    A callback to sync all distributed workers at a given frequency.
    Helpful when using distributed without DDP/FSDP but would still like to ensure that the workers are in sync with each other, for example large predict jobs.
    Note that only predict is supported at the moment.

    Args:
        sync_every_n_steps: the frequency at which to sync the workers.
    """

    def __init__(self, sync_every_n_steps: int = 1000) -> None:
        self.sync_every_n_steps = sync_every_n_steps

    def on_predict_step_end(self, state: State, unit: TPredictUnit) -> None:
        num_steps = unit.predict_progress.num_steps_completed
        if num_steps % self.sync_every_n_steps == 0:
            logger.info(f"Barrier at step {num_steps}")
            barrier()
