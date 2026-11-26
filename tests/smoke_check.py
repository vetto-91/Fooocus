"""Lightweight smoke checks for Fooocus (runs without GPU or downloaded models)."""

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_model_loader_security():
    from modules.model_loader import load_file_from_url

    with tempfile.TemporaryDirectory() as tmp:
        # Block non-HTTPS schemes
        try:
            load_file_from_url("http://huggingface.co/test.bin", model_dir=tmp, file_name="test.bin")
            raise AssertionError("Expected ValueError for HTTP URL")
        except ValueError:
            pass

        # Block untrusted LAN / SSRF hosts
        try:
            load_file_from_url("https://127.0.0.1/secret.bin", model_dir=tmp, file_name="secret.bin")
            raise AssertionError("Expected ValueError for untrusted host")
        except ValueError:
            pass

        # Block path traversal in file_name
        try:
            load_file_from_url("https://huggingface.co/lllyasviel/misc/resolve/main/x.bin", model_dir=tmp, file_name="../escape.bin")
            raise AssertionError("Expected ValueError for path traversal")
        except ValueError:
            pass


def test_path_traversal_guard():
    try:
        from modules.util import get_file_from_folder_list
    except ModuleNotFoundError as exc:
        print(f"Skipping test_path_traversal_guard (optional dep not installed locally: {exc.name})")
        return

    with tempfile.TemporaryDirectory() as tmp:
        try:
            get_file_from_folder_list("../../etc/passwd", [tmp])
            raise AssertionError("Expected ValueError for path traversal")
        except ValueError:
            pass

        ok_path = get_file_from_folder_list("model.safetensors", [tmp])
        assert os.path.commonpath([os.path.realpath(tmp), ok_path]) == os.path.realpath(tmp)


def test_html_escaping():
    from modules.html import make_progress_html

    rendered = make_progress_html(50, "<script>alert(1)</script>")
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_checkpoint_pickle_allowlist():
    import pickle
    import io
    from ldm_patched.modules.checkpoint_pickle import Unpickler

    # Builtin os.system must be rejected
    class Bad:
        def __reduce__(self):
            return (os.system, ("echo blocked",))

    payload = pickle.dumps(Bad())
    try:
        Unpickler(io.BytesIO(payload)).load()
        raise AssertionError("Expected UnpicklingError for os.system")
    except pickle.UnpicklingError:
        pass


if __name__ == "__main__":
    test_model_loader_security()
    test_path_traversal_guard()
    test_html_escaping()
    test_checkpoint_pickle_allowlist()
    print("ALL SMOKE CHECKS PASSED")
