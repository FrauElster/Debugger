from json import dumps

from Debugger.trace import trace, TraceLevel
from tets2 import i_will_return_smt


@trace(level=TraceLevel.ALL, packages="json")
def test_me():
    print("I will add 1 + 1")
    x = sum([1, 1])
    as_json = dumps({"sum": x})
    print(as_json)
    assert x == 2


class Harald:

    @trace()
    def introduce_self(self):
        return "Hi I`m Harald"


if __name__ == '__main__':
    test_me()
    i_will_return_smt(2)
    dumps({"diff": 5})
