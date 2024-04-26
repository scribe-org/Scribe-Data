import urllib.request
import sys
import time


def ping(url: str, timeout: int) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.getcode() == 200
    except (urllib.error.HTTPError, Exception) as err:
        print(f"{type(err).__name__}: {str(err)}", file=sys.stderr)
    return False
