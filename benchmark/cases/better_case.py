#!/usr/bin/ev python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""Example performance test using benchmark framework. Test react speed on amount of incoming messages using normal agent operating."""
import time

from benchmark.cases.helpers.dummy_handler import DummyHandler
from benchmark.framework.aea_test_wrapper import AEATestWrapper
from benchmark.framework.benchmark import BenchmarkControl
from benchmark.framework.cli import TestCli

from aea.configurations.base import SkillConfig


def make_agency_conf(name: str = "dummy_agent", skills_num: int = 1) -> dict:
    """Construct simple config for agency."""
    return {
        "name": "dummy_a",
        "skills": [
            {
                "config": SkillConfig(name=f"sc{i}"),  # type: ignore
                "handlers": {"dummy_handler": DummyHandler},
            }
            for i in range(skills_num)
        ],
    }


def react_speed_in_loop(
    benchmark: BenchmarkControl,
    agents_num: int = 2,
    skills_num: int = 1,
    inbox_num: int = 1000,
    agent_loop_timeout: float = 0.01,
):
    """Test inbox message processing in a loop."""
    aea_test_wrappers = []

    for i in range(agents_num):
        aea_test_wrapper = AEATestWrapper(**make_agency_conf(f"agent{i}", skills_num))
        aea_test_wrapper.set_loop_timeout(agent_loop_timeout)
        aea_test_wrappers.append(aea_test_wrapper)

        for _ in range(inbox_num):
            aea_test_wrapper.put_inbox(aea_test_wrapper.dummy_envelope())

    benchmark.start()

    for aea_test_wrapper in aea_test_wrappers:
        aea_test_wrapper.start_loop()

    try:
        while sum([not i.is_inbox_empty() for i in aea_test_wrappers]):
            time.sleep(0.1)

    finally:
        # wait to start, Race condition in case no messages to process
        while sum([not i.is_running() for i in aea_test_wrappers]):
            pass
        for aea_test_wrapper in aea_test_wrappers:
            aea_test_wrapper.stop_loop()


if __name__ == "__main__":
    TestCli(react_speed_in_loop).run()
