import os
from urllib.parse import urlparse
from typing import Optional

ALLOWED_MODEL_HOSTS = {
    "huggingface.co",
    "cdn-lfs.huggingface.co",
    "cdn-lfs-us-1.huggingface.co",
    "github.com",
    "objects.githubusercontent.com",
    "dl.fbaipublicfiles.com",
    "storage.googleapis.com",
}


def load_file_from_url(
        url: str,
        *,
        model_dir: str,
        progress: bool = True,
        file_name: Optional[str] = None,
) -> str:
    """Download a file from `url` into `model_dir`, using the file present if possible.

    Returns the path to the downloaded file.
    """
    domain = os.environ.get("HF_MIRROR", "https://huggingface.co").rstrip('/')
    url = str.replace(url, "https://huggingface.co", domain, 1)
    parsed_url = urlparse(url)
    allowed_hosts = set(ALLOWED_MODEL_HOSTS)
    mirror_host = urlparse(domain).hostname
    if mirror_host:
        allowed_hosts.add(mirror_host.lower())
    if parsed_url.scheme != 'https':
        raise ValueError(f'Unsupported URL scheme for model download (HTTPS required): {parsed_url.scheme}')
    if not parsed_url.hostname or parsed_url.hostname.lower() not in allowed_hosts:
        raise ValueError(f'Blocked model download from untrusted host: {parsed_url.hostname}')
    os.makedirs(model_dir, exist_ok=True)
    if not file_name:
        file_name = os.path.basename(parsed_url.path)
    model_dir_abs = os.path.abspath(os.path.realpath(model_dir))
    cached_file = os.path.abspath(os.path.realpath(os.path.join(model_dir_abs, file_name)))
    if os.path.commonpath([model_dir_abs, cached_file]) != model_dir_abs:
        raise ValueError(f'Path traversal detected in model file name: {file_name}')
    if not os.path.exists(cached_file):
        print(f'Downloading: "{url}" to {cached_file}\n')
        from torch.hub import download_url_to_file
        download_url_to_file(url, cached_file, progress=progress)
    return cached_file
