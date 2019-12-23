import functools
import inspect
import sys
from enum import Enum, auto
from typing import Union, Callable, List, Tuple, Any, Set


class tracelevel(Enum):
    MINIMAL = auto()
    SOME = auto()
    ALL = auto()


class trace:
    def __init__(self, tracelevel: tracelevel = tracelevel.ALL, packages: Union[str, list] = None):
        self.packages: List[str] = ["__main__"]

        if isinstance(packages, str):
            self.packages.append(packages)
        if isinstance(packages, list):
            self.packages.extend(packages)

    def __call__(self, func: Callable, *args, **kwargs):
        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            # members = dict(inspect.getmembers(func))
            # annotations: List[str] = members["__annotations__"]
            # func_name: str = members["__code__"].co_name
            # functions: Tuple[str] = members["__code__"].co_names

            objects_to_patch = self._get_objects_to_patch()
            self._patch_objects(objects_to_patch)

            result = func(*args, **kwargs)

            self._unpatch_objects(objects_to_patch)

            return result

        return wrapper_func

    def _patch_objects(self, objects: List[Tuple[Any, Any]]):
        for module, obj in objects:
            if inspect.isclass(obj):
                continue
            if inspect.isfunction(obj):
                self._patch_function(func=obj, module=module)

    def _patch_function(self, func: Any, module: Any):
        @functools.wraps(func)
        def patched_function(*args, **kwargs):
            print(f'{func.__name__}: {", ".join(map(str, args))} {", ".join(kwargs)}')
            return func(*args, **kwargs)

        setattr(module, func.__name__, patched_function)

    def _unpatch_objects(self, objects):
        for module, obj in objects:
            if inspect.isclass(obj):
                continue
            if inspect.isfunction(obj):
                self._unpatch_function(obj, module)

    def _unpatch_function(self, func, module):
        setattr(module, func.__name__, func)

    def _get_objects_to_patch(self) -> List[Tuple[Any, Any]]:
        modules = {mod: val for mod, val in sys.modules.items() if mod in self.packages}
        result: List[Tuple[Any, Any]] = []
        for importing_module_name in modules:
            mod_insp = {name: member for name, member in inspect.getmembers(modules[importing_module_name]) if
                        not name.startswith("__")}
            for member in mod_insp.values():
                member_data = dict(inspect.getmembers(member))

                if "__module__" not in member_data:
                    continue

                module_name: str = member_data["__module__"]
                if module_name in self.packages:
                    result.append((modules[importing_module_name], member))
        return result
