from functools import wraps

def spam_metrics(test_fn):
    @wraps(test_fn)
    def wrapper(*args, **kwargs):
        metrics = {
            "false_pos": 0,
            "false_neg": 0,
            "total": 0,
            "correct": 0,
        }

        def record(expected_is_spam: bool, predicted_is_spam: bool):
            metrics["total"] += 1
            if expected_is_spam == predicted_is_spam:
                metrics["correct"] += 1
            else:
                if predicted_is_spam and not expected_is_spam:
                    metrics["false_pos"] += 1
                elif not predicted_is_spam and expected_is_spam:
                    metrics["false_neg"] += 1

        wrapper._record = record
        try:
            test_fn(*args, **kwargs)
        finally:
            accuracy = (
                metrics["correct"] / metrics["total"]
                if metrics["total"] > 0
                else 0
            )

            print(
                f"\n{test_fn.__name__} metrics:"
                f"\n  accuracy       : {accuracy:.2%}"
                f"\n  false positives: {metrics['false_pos']}"
                f"\n  false negatives: {metrics['false_neg']}"
                f"\n  total samples  : {metrics['total']}\n"
            )

    return wrapper