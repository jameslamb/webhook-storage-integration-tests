"""
Sample flow used to test storage configured with
stored_as_script=True.
"""
import random

import prefect
from prefect import task, Flow

FLOW_NAME = "test-flow"


@task
def random_number():
    logger = prefect.context.get("logger")
    num = random.randint(0, 100)
    logger.info(f"random number: {num}")
    return num


with Flow(FLOW_NAME) as flow:
    r = random_number()
