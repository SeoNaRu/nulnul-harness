#!/usr/bin/env python3
import json
from pathlib import Path

codes = json.loads(Path("contracts/error-codes.json").read_text(encoding="utf-8"))
assert isinstance(codes, list) and codes == sorted(set(codes))
assert all(isinstance(code, str) and code for code in codes)
print("error catalog verified")
