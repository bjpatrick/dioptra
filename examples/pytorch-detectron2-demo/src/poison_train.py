#!/usr/bin/env python
# This Software (Dioptra) is being made available as a public service by the
# National Institute of Standards and Technology (NIST), an Agency of the United
# States Department of Commerce. This software was developed in part by employees of
# NIST and in part by NIST contractors. Copyright in portions of this software that
# were developed by NIST contractors has been licensed or assigned to NIST. Pursuant
# to Title 17 United States Code Section 105, works of NIST employees are not
# subject to copyright protection in the United States. However, NIST may hold
# international copyright in software created by its employees and domestic
# copyright (or licensing rights) in portions of software that were assigned or
# licensed to NIST. To the extent that NIST holds copyright in this software, it is
# being made available under the Creative Commons Attribution 4.0 International
# license (CC BY 4.0). The disclaimers of the CC BY 4.0 license apply to all parts
# of the software developed or licensed by NIST.
#
# ACCESS THE FULL CC BY 4.0 LICENSE HERE:
# https://creativecommons.org/licenses/by/4.0/legalcode
import os
from typing import Any, Dict, List

import click
import mlflow
import structlog
from prefect import Flow, Parameter
from prefect.utilities.logging import get_logger as get_prefect_logger
from structlog.stdlib import BoundLogger

from dioptra import pyplugs
from dioptra.sdk.utilities.contexts import plugin_dirs
from dioptra.sdk.utilities.logging import (
    StderrLogStream,
    StdoutLogStream,
    attach_stdout_stream_handler,
    clear_logger_handlers,
    configure_structlog,
    set_logging_level,
)

_PLUGINS_IMPORT_PATH: str = "dioptra_builtins"
_CUSTOM_PLUGINS_IMPORT_PATH: str = "dioptra_custom"


LOGGER: BoundLogger = structlog.stdlib.get_logger()
PERFORMANCE_METRICS: List[Dict[str, Any]] = [
    {"name": "CategoricalAccuracy", "parameters": {"name": "accuracy"}},
    {"name": "Precision", "parameters": {"name": "precision"}},
    {"name": "Recall", "parameters": {"name": "recall"}},
    {"name": "AUC", "parameters": {"name": "auc"}},
]
def _coerce_comma_separated_values(ctx, param, value):
    return list((x.strip()) for x in value.split(","))

def _coerce_comma_separated_values_int(ctx, param, value):
    return list(int(x.strip()) for x in value.split(","))

def _coerce_comma_separated_values_float(ctx, param, value):
    return list(float(x.strip()) for x in value.split(","))

@click.command()
@click.option(
    "--data-dir-train",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True, readable=True
    ),
    help="Root directory for NFS mounted training dataset (in container).",
)
@click.option(
    "--data-dir-test",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True, readable=True
    ),
    help="Root directory for NFS mounted testing dataset (in container).",
)
@click.option(
    "--model-architecture",
    type=click.STRING,
    default="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
    help="Model architecture",
)
@click.option(
    "--bbox-conf-threshold",
    type=click.FLOAT,
    default=0.7,
    help="Confidence threshold for bounding box results during testing.",
)
@click.option(
    "--dataset-type",
    type=click.Choice(["detectron2_balloon_json", "pasal_voc"], case_sensitive=False),
    default="detectron2_balloon_json",
    help="Type of label file used by dataset",
)
@click.option(
    "--class-names",
    type=click.STRING,
    callback=_coerce_comma_separated_values,
    help="Comma separated list of class values.",
)
@click.option(
    "--poison-class-label",
    type=click.INT,
    help="Target intended class label for poison.",
    default=1
)
@click.option(
    "--poison-class-target",
    type=click.INT,
    help="Original target class for poisoning. Any bounding box with specified label will be watermarked and altered to poison_class_label.",
    default=0
)
@click.option(
    "--poison-scale",
    type=click.FLOAT,
    help="Relative scaling of poison vs bounding box.",
    default=0.2
)
@click.option(
    "--poison-color",
    type=click.STRING,
    callback=_coerce_comma_separated_values_int,
    help="RGB color values of poison, separated by commas",
    default="0,255,255"
)
@click.option(
    "--poison-rel-x-location",
    type=click.FLOAT,
    help="Relative horizontal starting point of poison, located within bounding box.",
    default=0.5
)
@click.option(
    "--poison-rel-y-location",
    type=click.FLOAT,
    help="Relative vertical starting point of poison, located within bounding box.",
    default=0.5
)
@click.option(
    "--dataloader-num-workers",
    type=click.INT,
    help="Number of dataloader workers for training.",
    default=4,
)
@click.option(
    "--batch-size",
    type=click.INT,
    help="Batch size to use when training a single epoch",
    default=32,
)
@click.option(
    "--max-iter",
    type=click.INT,
    help="Maximum number of training steps.",
    default=300,
)
@click.option(
    "--register-model-name",
    type=click.STRING,
    default="",
    help=(
        "Register the trained model under the provided name. If an empty string, "
        "then the trained model will not be registered."
    ),
)
@click.option(
    "--learning-rate",
    type=click.FLOAT,
    help="Model learning rate",
    default=0.00025
)
@click.option(
    "--gpu",
    type=click.BOOL,
    help="Enables GPU-acceleration.",
    default=False,
)
@click.option(
    "--seed",
    type=click.INT,
    help="Set the entry point rng seed",
    default=-1,
)
@click.option(
    "--poison",
    type=click.BOOL,
    help="Flag for to enable poisoning in task plugins",
    default=False,
)
def poison_train(
    data_dir_train,
    data_dir_test,
    dataset_type,
    model_architecture,
    bbox_conf_threshold,
    class_names,
    poison_class_label,
    poison_class_target,
    poison_scale,
    poison_color,
    poison_rel_x_location,
    poison_rel_y_location,
    batch_size,
    register_model_name,
    learning_rate,
    max_iter,
    dataloader_num_workers,
    gpu,
    seed,
    poison
):
    LOGGER.info(
        "Execute MLFlow entry point",
        entry_point="train",
        data_dir_train=data_dir_train,
        data_dir_test=data_dir_test,
        dataset_type=dataset_type,
        model_architecture=model_architecture,
        bbox_conf_threshold=bbox_conf_threshold,
        class_names=class_names,
        batch_size=batch_size,
        register_model_name=register_model_name,
        learning_rate=learning_rate,
        max_iter=max_iter,
        dataloader_num_workers=dataloader_num_workers,
        poison_class_label=poison_class_label,
        poison_class_target=poison_class_target,
        poison_scale=poison_scale,
        poison_color=poison_color,
        poison_rel_x_location=poison_rel_x_location,
        poison_rel_y_location=poison_rel_y_location,
        gpu=gpu,
        seed=seed,
        poison=poison
    )

    with mlflow.start_run() as active_run:
        flow: Flow = init_train_flow()
        state = flow.run(
            parameters=dict(
                active_run=active_run,
                data_dir_train=data_dir_train,
                data_dir_test=data_dir_test,
                dataset_type=dataset_type,
                model_architecture=model_architecture,
                bbox_conf_threshold=bbox_conf_threshold,
                class_names=class_names,
                batch_size=batch_size,
                register_model_name=register_model_name,
                learning_rate=learning_rate,
                max_iter=max_iter,
                dataloader_num_workers=dataloader_num_workers,
                poison_class_label=poison_class_label,
                poison_class_target=poison_class_target,
                poison_scale=poison_scale,
                poison_color=poison_color,
                poison_rel_x_location=poison_rel_x_location,
                poison_rel_y_location=poison_rel_y_location,
                gpu=gpu,
                seed=seed,
                poison= poison
            )
        )

    return state


def init_train_flow() -> Flow:
    with Flow("Train Model") as flow:
        (
            active_run,
            data_dir_train,
            data_dir_test,
            dataset_type,
            model_architecture,
            bbox_conf_threshold,
            class_names,
            batch_size,
            register_model_name,
            learning_rate,
            max_iter,
            dataloader_num_workers,
            poison_class_label,
            poison_class_target,
            poison_scale,
            poison_color,
            poison_rel_x_location,
            poison_rel_y_location,
            gpu,
            seed,
            poison
        ) = (
            Parameter("active_run"),
            Parameter("data_dir_train"),
            Parameter("data_dir_test"),
            Parameter("dataset_type"),
            Parameter("model_architecture"),
            Parameter("bbox_conf_threshold"),
            Parameter("class_names"),
            Parameter("batch_size"),
            Parameter("register_model_name"),
            Parameter("learning_rate"),
            Parameter("max_iter"),
            Parameter("dataloader_num_workers"),
            Parameter("poison_class_label"),
            Parameter("poison_class_target"),
            Parameter("poison_scale"),
            Parameter("poison_color"),
            Parameter("poison_rel_x_location"),
            Parameter("poison_rel_y_location"),
            Parameter("gpu"),
            Parameter("seed"),
            Parameter("poison")
        )
        seed, rng = pyplugs.call_task(
            f"{_PLUGINS_IMPORT_PATH}.random", "rng", "init_rng", seed=seed
        )
        dataset_seed = pyplugs.call_task(
            f"{_PLUGINS_IMPORT_PATH}.random", "sample", "draw_random_integer", rng=rng
        )

        log_mlflow_params_result = pyplugs.call_task(  # noqa: F841
            f"{_PLUGINS_IMPORT_PATH}.tracking",
            "mlflow",
            "log_parameters",
            parameters=dict(
                entry_point_seed=seed,
                dataset_seed=dataset_seed,
            ),
        )

        train_ds_meta = pyplugs.call_task(
            f"{_CUSTOM_PLUGINS_IMPORT_PATH}.pytorch_d2",
            "data_detectron2",
            "register_dataset",
            dataset_name="data_train",
            dataset_path=data_dir_train,
            dataset_type=dataset_type,
            class_names=class_names,
            poison=poison,
            poison_class_label=poison_class_label,
            poison_class_target=poison_class_target,
            poison_scale=poison_scale,
            poison_color=poison_color,
            poison_rel_x_location=poison_rel_x_location,
            poison_rel_y_location=poison_rel_y_location,
            upstream_tasks=[log_mlflow_params_result]
        )

        test_ds_meta_poison = pyplugs.call_task(  # noqa: F841
            f"{_CUSTOM_PLUGINS_IMPORT_PATH}.pytorch_d2",
            "data_detectron2",
            "register_dataset",
            dataset_name="data_test_poison",
            dataset_path=data_dir_test,
            dataset_type=dataset_type,
            class_names=class_names,
            poison=poison,
            testing=poison,
            poison_class_label=poison_class_label,
            poison_class_target=poison_class_target,
            poison_scale=poison_scale,
            poison_color=poison_color,
            poison_rel_x_location=poison_rel_x_location,
            poison_rel_y_location=poison_rel_y_location,
            upstream_tasks=[log_mlflow_params_result]
        )

        test_ds_meta = pyplugs.call_task(
            f"{_CUSTOM_PLUGINS_IMPORT_PATH}.pytorch_d2",
            "data_detectron2",
            "register_dataset",
            dataset_name="data_test",
            dataset_path=data_dir_test,
            dataset_type=dataset_type,
            class_names=class_names,
            upstream_tasks=[log_mlflow_params_result]
        )

        classifier, config = pyplugs.call_task(
            f"{_CUSTOM_PLUGINS_IMPORT_PATH}.pytorch_d2",
            "train_detectron2",
            "train_model",
            dataset_name="data_train",
            class_names=class_names,
            model_architecture=model_architecture,
            batch_size=batch_size,
            learning_rate=learning_rate,
            max_iter=max_iter,
            dataloader_num_workers=dataloader_num_workers,
            gpu=gpu,
            upstream_tasks=[train_ds_meta, test_ds_meta]
        )

        eval_results = pyplugs.call_task(
            f"{_CUSTOM_PLUGINS_IMPORT_PATH}.pytorch_d2",
            "eval_detectron2",
            "eval_dataset",
            dataset_name="data_test",
            classifier=classifier,
            confidence=bbox_conf_threshold,
            cfg=config
        )

        eval_results_poison = pyplugs.call_task(
            f"{_CUSTOM_PLUGINS_IMPORT_PATH}.pytorch_d2",
            "eval_detectron2",
            "eval_dataset",
            dataset_name="data_test_poison",
            classifier=classifier,
            confidence=bbox_conf_threshold,
            cfg=config,
            poison=poison
        )

        log_classifier_performance_metrics_result = pyplugs.call_task(  # noqa: F841
            f"{_PLUGINS_IMPORT_PATH}.tracking",
            "mlflow",
            "log_metrics",
            metrics=eval_results,
        )

        log_classifier_performance_metrics_result = pyplugs.call_task(  # noqa: F841
            f"{_PLUGINS_IMPORT_PATH}.tracking",
            "mlflow",
            "log_metrics",
            metrics=eval_results_poison,
        )

        log_classifier_performance_metrics_result = pyplugs.call_task(  # noqa: F841
            f"{_CUSTOM_PLUGINS_IMPORT_PATH}.pytorch_d2",
            "registry_mlflow_detectron2",
            "add_model_to_registry",
            active_run=active_run,
            name=register_model_name,
            model_dir="output",
            upstream_tasks=[classifier]
        )

    return flow


if __name__ == "__main__":
    log_level: str = os.getenv("DIOPTRA_JOB_LOG_LEVEL", default="INFO")
    as_json: bool = True if os.getenv("DIOPTRA_JOB_LOG_AS_JSON") else False

    clear_logger_handlers(get_prefect_logger())
    attach_stdout_stream_handler(as_json)
    set_logging_level(log_level)
    configure_structlog()

    with plugin_dirs(), StdoutLogStream(as_json), StderrLogStream(as_json):
        _ = poison_train()