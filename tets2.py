from typing import Any

from Debugger.trace import trace, tracelevel


@trace(level=tracelevel.ALL, packages="json")
def i_will_return_smt(x: Any):
    print(f"Returning {x}")
    return x
