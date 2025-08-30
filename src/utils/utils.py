import base64


def encode(s: str) -> str:
    return str(base64.b64encode(bytes(s, encoding='utf-8')), encoding='utf-8')

def decode(s: str) -> str:
    return str(base64.b64decode(bytes(s, encoding='utf-8')), encoding='utf-8')