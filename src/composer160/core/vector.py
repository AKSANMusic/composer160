"""COMPOSER-160 Parameter Vector.

Manages the 160-slot parameter dictionary, tracking value assignments,
assumed vs locked fields, and T1 completeness.
"""

import copy
import json
from pathlib import Path
from typing import Any

from composer160.core.parameters import PARAMETER_REGISTRY, T1_PARAMETER_IDS
from composer160.core.types import Tier


class ParameterVector:
    """Manages a 160-slot parameter vector for musical direction.

    Maintains private state for values, assumed parameters (statistically
    inferred), and locked parameters (explicitly set by user or preset).
    """

    def __init__(self) -> None:
        self._values: dict[int, Any] = {}
        self._assumed: dict[int, Any] = {}
        self._locked: dict[int, Any] = {}

    def set(self, param_id: int, value: Any, assumed: bool = False) -> None:
        """Assign a parameter value.

        Args:
            param_id: Parameter index (1–160).
            value: The assigned value.
            assumed: Whether this value was assumed/inferred rather than explicitly chosen.

        Raises:
            ValueError: If param_id is outside the legal range [1, 160].
        """
        if not (1 <= param_id <= 160):
            raise ValueError(f"param_id must be between 1 and 160, got {param_id}")

        self._values[param_id] = value
        if assumed:
            self._assumed[param_id] = value
            self._locked.pop(param_id, None)
        else:
            self._locked[param_id] = value
            self._assumed.pop(param_id, None)

    def get(self, param_id: int) -> Any:
        """Retrieve the value of a parameter.

        Returns the assigned value, or the parameter's default ("auto")
        if unset.
        """
        if not (1 <= param_id <= 160):
            raise ValueError(f"param_id must be between 1 and 160, got {param_id}")

        if param_id in self._values:
            return self._values[param_id]

        defn = PARAMETER_REGISTRY.get(param_id)
        return defn.default if defn is not None else "auto"

    def is_set(self, param_id: int) -> bool:
        """Check whether a parameter has been explicitly set to a non-auto value."""
        return param_id in self._values and self._values[param_id] != "auto"

    def t1_complete(self) -> bool:
        """Verify whether all 12 Tier-1 (T1) parameters are populated."""
        return all(self.is_set(pid) for pid in T1_PARAMETER_IDS)

    def assumed_t1_fields(self) -> list[tuple[int, str, Any]]:
        """Return all assumed T1 parameters as (param_id, name, value) tuples.

        Used to construct the mandatory one-line assumptions note in engine output.
        """
        assumed_list: list[tuple[int, str, Any]] = []
        for pid in T1_PARAMETER_IDS:
            if pid in self._assumed and self.is_set(pid):
                defn = PARAMETER_REGISTRY.get(pid)
                name = defn.name if defn is not None else f"Param {pid}"
                assumed_list.append((pid, name, self._values[pid]))
        return assumed_list

    def copy(self) -> "ParameterVector":
        """Create a deep copy of this parameter vector."""
        new_vec = ParameterVector()
        new_vec._values = copy.deepcopy(self._values)
        new_vec._assumed = copy.deepcopy(self._assumed)
        new_vec._locked = copy.deepcopy(self._locked)
        return new_vec

    def to_dict(self) -> dict[str, Any]:
        """Serialize the vector state to a dictionary suitable for JSON export."""
        serialized_values: dict[str, Any] = {}
        for pid, val in self._values.items():
            if pid == 130 and isinstance(val, (list, tuple)):
                # Convert tuples to lists for pure JSON compatibility
                serialized_values[str(pid)] = [
                    list(item) if isinstance(item, (list, tuple)) else item
                    for item in val
                ]
            else:
                serialized_values[str(pid)] = val

        return {
            "format": "c160",
            "version": "1.0",
            "values": serialized_values,
            "assumed": sorted(list(self._assumed.keys())),
            "locked": sorted(list(self._locked.keys())),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParameterVector":
        """Deserialize a dictionary into a ParameterVector."""
        if not isinstance(data, dict):
            raise ValueError(f"Invalid format: expected dict, got {type(data).__name__}")
        if data.get("format") != "c160":
            raise ValueError(
                f"Unsupported format: expected 'c160', got {data.get('format')!r}"
            )

        vec = cls()
        values = data.get("values", {})
        assumed_keys = set(int(k) for k in data.get("assumed", []))
        locked_keys = set(int(k) for k in data.get("locked", []))

        for pid_str, val in values.items():
            try:
                pid = int(pid_str)
            except ValueError:
                continue
            if not (1 <= pid <= 160):
                continue

            # Restore section map tuples if parameter 130
            if pid == 130 and isinstance(val, list):
                val = [
                    (str(item[0]), int(item[1]))
                    if isinstance(item, (list, tuple)) and len(item) >= 2
                    else item
                    for item in val
                ]

            vec._values[pid] = val
            if pid in assumed_keys:
                vec._assumed[pid] = val
            else:
                vec._locked[pid] = val

        return vec

    def save_to_file(self, filepath: str | Path) -> None:
        """Save the parameter vector to a .c160 JSON file.

        Args:
            filepath: Path to the target file.

        Raises:
            OSError: If writing to the file fails.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str | Path) -> "ParameterVector":
        """Load a parameter vector from a .c160 JSON file.

        Args:
            filepath: Path to the .c160 file.

        Returns:
            A reconstructed ParameterVector.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file contains invalid JSON or schema.
        """
        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed .c160 JSON file: {exc}") from exc

        return cls.from_dict(data)

    def to_compact(self) -> str:
        """Render this vector in compact bracket notation."""
        from composer160.output.notation import render_vector
        return render_vector(self)

    def __len__(self) -> int:
        """Return the number of currently set parameters."""
        return len(self._values)

    def __repr__(self) -> str:
        set_count = len([v for v in self._values.values() if v != "auto"])
        assumed_count = len(self._assumed)
        return (
            f"<ParameterVector: {set_count}/160 set, "
            f"{assumed_count} assumed, T1 complete={self.t1_complete()}>"
        )
