from openeval.domain.evaluation import EvaluationDefinition


def test_evaluation_definition_can_be_created():
    evaluation = EvaluationDefinition(
        id="eval-1",
        name="Demo Evaluation",
        dataset_version_id="dataset-v1",
        prompt_version_id="prompt-v1",
        target={"provider": "openai", "model": "gpt-4o"},
        metric_plugins=[{"name": "accuracy"}],
    )

    assert evaluation.id == "eval-1"
    assert evaluation.name == "Demo Evaluation"
    assert evaluation.dataset_version_id == "dataset-v1"
