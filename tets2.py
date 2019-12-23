from typing import Any

from Debugger.main import trace, tracelevel


@trace(tracelevel=tracelevel.ALL, packages="json")
def i_will_return_smt(x: Any):
    print(f"Returning {x}")
    return x
