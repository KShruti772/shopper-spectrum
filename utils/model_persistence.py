"""Model persistence utilities for Shopper Spectrum.

Provides functions to save and load models and preprocessing artifacts using pickle,
and a small standardized directory layout for model versions.

Best practices used:
- Use binary pickle with highest protocol for efficiency.
- Store artifacts in a versioned directory: `models/{model_name}_{version}/`.
- Save a simple JSON metadata file alongside artifacts.
- Provide clear error messages and checks.
"""

from pathlib import Path
import pickle
import json
from datetime import datetime
from typing import Any, Tuple


def save_pickle(obj: Any, path: Path) -> None:
    """Save an object to `path` using pickle with highest protocol."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(path: Path) -> Any:
    """Load a pickle object from `path`."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Pickle file not found: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)


def save_artifacts(scaler: Any, model: Any, base_dir: Path, model_name: str = "kmeans", version: str = "v1") -> Path:
    """Save scaler and model into a versioned directory.

    Directory layout:
        base_dir/{model_name}_{version}/
            scaler.pkl
            model.pkl
            metadata.json

    Returns the path to the artifact directory.
    """
    base_dir = Path(base_dir)
    artifact_dir = base_dir / f"{model_name}_{version}"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    scaler_path = artifact_dir / "scaler.pkl"
    model_path = artifact_dir / "model.pkl"
    metadata_path = artifact_dir / "metadata.json"

    save_pickle(scaler, scaler_path)
    save_pickle(model, model_path)

    metadata = {
        "model_name": model_name,
        "version": version,
        "saved_at": datetime.utcnow().isoformat() + "Z",
        "scaler_file": str(scaler_path.name),
        "model_file": str(model_path.name),
    }
    with open(metadata_path, "w", encoding="utf8") as f:
        json.dump(metadata, f, indent=2)

    return artifact_dir


def load_artifacts(artifact_dir: Path) -> Tuple[Any, Any, dict]:
    """Load scaler and model from the artifact directory. Returns (scaler, model, metadata)."""
    artifact_dir = Path(artifact_dir)
    if not artifact_dir.exists():
        raise FileNotFoundError(f"Artifact directory not found: {artifact_dir}")

    metadata_path = artifact_dir / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"metadata.json not found in {artifact_dir}")

    with open(metadata_path, "r", encoding="utf8") as f:
        metadata = json.load(f)

    scaler_path = artifact_dir / metadata.get("scaler_file", "scaler.pkl")
    model_path = artifact_dir / metadata.get("model_file", "model.pkl")

    scaler = load_pickle(scaler_path)
    model = load_pickle(model_path)

    return scaler, model, metadata


def predict_with_artifacts(artifact_dir: Path, sample_rfm) -> Tuple[int, Any]:
    """Load artifacts and predict cluster for a sample RFM input.

    sample_rfm can be a list-like (Recency, Frequency, Monetary) or dict with keys.
    Returns (predicted_label, model) so caller can inspect the model if needed.
    """
    scaler, model, metadata = load_artifacts(Path(artifact_dir))

    # Normalize sample to 2D array
    if isinstance(sample_rfm, dict):
        ordered = [sample_rfm.get("Recency"), sample_rfm.get("Frequency"), sample_rfm.get("Monetary")]
        sample_arr = [ordered]
    else:
        sample_arr = [list(sample_rfm)]

    X_scaled = scaler.transform(sample_arr)
    label = model.predict(X_scaled)[0]
    return int(label), model


if __name__ == "__main__":
    print("This module provides save/load helpers for ML artifacts. Import functions in your scripts.")
