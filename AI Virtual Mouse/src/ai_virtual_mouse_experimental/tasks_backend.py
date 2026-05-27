from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from urllib.request import urlopen
import shutil

from .config import ExperimentalConfig


DEFAULT_HAND_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)


class BackendError(RuntimeError):
    """Raised when a hand tracking backend cannot be prepared or initialized."""


@dataclass(frozen=True)
class TasksBackendMetadata:
    api_family: str
    backend: str
    model_path: str
    model_url: str
    model_exists: bool
    auto_download_model: bool


def resolve_model_path(model_path: str, project_root: Path | None = None) -> Path:
    path = Path(model_path)
    if path.is_absolute():
        return path
    return (project_root or Path.cwd()) / path


def build_tasks_backend_metadata(
    config: ExperimentalConfig, project_root: Path | None = None
) -> TasksBackendMetadata:
    model_path = resolve_model_path(config.backend.model_path, project_root)
    return TasksBackendMetadata(
        api_family="mediapipe_tasks",
        backend="hand_landmarker",
        model_path=str(model_path),
        model_url=config.backend.model_url,
        model_exists=model_path.exists(),
        auto_download_model=config.backend.auto_download_model,
    )


def download_hand_landmarker_model(
    config: ExperimentalConfig,
    project_root: Path | None = None,
    overwrite: bool = False,
) -> Path:
    model_path = resolve_model_path(config.backend.model_path, project_root)
    if model_path.exists() and not overwrite:
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(config.backend.model_url, timeout=60) as response, model_path.open("wb") as output:
            shutil.copyfileobj(response, output)
    except Exception as exc:  # pragma: no cover - network failures are environment-specific.
        raise BackendError(f"Failed to download HandLandmarker model: {exc}") from exc

    if not model_path.exists() or model_path.stat().st_size == 0:
        raise BackendError(f"Downloaded model is empty or missing: {model_path}")

    return model_path


def ensure_hand_landmarker_model(
    config: ExperimentalConfig,
    project_root: Path | None = None,
    overwrite: bool = False,
) -> Path:
    model_path = resolve_model_path(config.backend.model_path, project_root)
    if model_path.exists() and not overwrite:
        return model_path

    if not config.backend.auto_download_model and not overwrite:
        raise BackendError(
            f"HandLandmarker model not found: {model_path}. "
            "Run with --download-model or enable backend.auto_download_model."
        )

    return download_hand_landmarker_model(config, project_root, overwrite=overwrite)


def smoke_test_tasks_backend(config: ExperimentalConfig, project_root: Path | None = None) -> TasksBackendMetadata:
    model_path = ensure_hand_landmarker_model(config, project_root)

    try:
        tasks_python = import_module("mediapipe.tasks.python")
        vision = import_module("mediapipe.tasks.python.vision")
        options = vision.HandLandmarkerOptions(
            base_options=tasks_python.BaseOptions(model_asset_path=str(model_path)),
            num_hands=1,
        )
        landmarker = vision.HandLandmarker.create_from_options(options)
        close = getattr(landmarker, "close", None)
        if callable(close):
            close()
    except ModuleNotFoundError as exc:
        raise BackendError(
            "MediaPipe Tasks API is not installed. Install project requirements before "
            "running the improved backend."
        ) from exc
    except Exception as exc:
        raise BackendError(f"MediaPipe Tasks backend smoke test failed: {exc}") from exc

    return build_tasks_backend_metadata(config, project_root)
