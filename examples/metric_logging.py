from mltrace import Task
from sklearn.metrics import mean_squared_error

import random
import string

task = Task("testing")


def inference_component(output_id):
    task.logOutput(random.random(), output_id)


def feedback_component(output_id):
    task.logFeedback(random.randint(0, 1), output_id)


if __name__ == "__main__":

    for _ in range(5):
        output_id = "".join(
            random.choice(string.ascii_uppercase) for _ in range(10)
        )

        inference_component(output_id)
        feedback_component(output_id)

    # Compute accuracy
    print(task.computeMetric("roc_auc"))
