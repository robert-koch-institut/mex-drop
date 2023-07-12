import base64

from mex.drop.security import generate_token


def test_generate_token(capsys):
    generate_token()
    captured_out = capsys.readouterr().out
    bytes_out = base64.urlsafe_b64decode(("b=" + captured_out.strip()).encode("ascii"))
    assert len(bytes_out) >= 32
