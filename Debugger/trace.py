import functools
import inspect
import logging
import sys
from typing import Union, Callable, List, Tuple, Any

from .export import TraceExporter
from .types import TraceLevel, TraceRecord, TimeProvider, SystemTimeProvider

LOGGER = logging.getLogger(__name__)


class trace:
    """
    The actual decorator class
    """

    def __init__(self, level: TraceLevel = TraceLevel.ALL, packages: Union[str, list] = None,
                 exporter: TraceExporter = None, time_provider: TimeProvider = None):
        self.level = level
        self.module_names: List[str] = []
        self.exporter = exporter
        self.time_provider = time_provider if time_provider is not None else SystemTimeProvider()
        self.records: List[TraceRecord] = []

        if isinstance(packages, str):
            self.module_names.append(packages)
        if isinstance(packages, list):
            self.module_names.extend(packages)

    def __call__(self, func: Callable, *args, **kwargs):
        """
        This method gets executed if the wrapped function is called
        :param func: the function to wrap
        :param args: args of the function to wrap
        :param kwargs: kwargs of the function to wrap
        :return: the wrapped function
        """
        # add the module where the function is defined in
        function_module = inspect.getmodule(func)
        if function_module is None:
            LOGGER.warning(f'getmodule of {func} returned None')
            return func
        self.module_names.append(function_module.__name__)

        @functools.wraps(func)
        def wrapper_func(*args, **kwargs):
            objects_to_patch = self._get_objects_to_patch()
            self._patch_objects(objects_to_patch)

            result = self._call_function(func, args, kwargs)

            self._unpatch_objects(objects_to_patch)
            self._persist_trace_results()
            return result

        return wrapper_func

    def _call_function(self, func: Any, args, kwargs):
        """
        Calls a given function and wraps it within a trace record
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        start_time = self.time_provider.get_current_time()
        record = TraceRecord(func.__name__, args, kwargs, start_time)
        self.records.append(record)

        result = func(*args, **kwargs)

        end_time = self.time_provider.get_current_time()
        record.end_time = end_time

        return result

    def _patch_objects(self, objects: List[Tuple[Any, Any]]) -> None:
        """
        Patches any callable to inject tracer behaviour
        :param objects: List of Tuples with <Module, class / function>
        :return: None
        """
        for module, obj in objects:
            if inspect.isclass(obj):
                continue
            if inspect.isfunction(obj):
                self._patch_function(func=obj, module=module)

    def _patch_function(self, func: Any, module: Any) -> None:
        """
        Monkey patches a function to inject tracer behaviour
        :param func: the function to patch
        :param module: the module the function is implemented in
        :return: None
        """

        @functools.wraps(func)
        def patched_function(*args, **kwargs):
            return self._call_function(func, args, kwargs)

        setattr(module, func.__name__, patched_function)

    def _unpatch_objects(self, objects: List[Tuple[Any, Any]]) -> None:
        """
        sets any object back to its original implementation
        :param objects: a list of tuples containing <Module, class / function>
        :return: None
        """
        for module, obj in objects:
            if inspect.isclass(obj):
                continue
            if inspect.isfunction(obj):
                self._unpatch_function(obj, module)

    def _unpatch_function(self, func, module) -> None:
        """
        sets a function back to its original behaviour
        :param func: the function to unpatch
        :param module: the corresponding module where the default implementation is
        :return: None
        """
        setattr(module, func.__name__, func)

    def _get_objects_to_patch(self) -> List[Tuple[Any, Any]]:
        """
        Filters out every imported module that is listed in self.module_names
        :return: a List containing tuples with <Module, Class / Function>
        """
        modules = {mod: val for mod, val in sys.modules.items() if mod in self.module_names}
        result: List[Tuple[Any, Any]] = []
        for importing_module_name in modules:
            mod_insp = {name: member for name, member in
                        inspect.getmembers(modules[importing_module_name]) if
                        not name.startswith("__")}
            for member in mod_insp.values():
                member_data = dict(inspect.getmembers(member))

                if "__module__" not in member_data:
                    # i m not quiet sure, but i think we did this to ignore built ins
                    continue

                module_name: str = member_data["__module__"]
                if module_name in self.module_names:
                    result.append((modules[importing_module_name], member))
        return result

    def _persist_trace_results(self):
        """
        Calls the callback of persistor
        :return: None
        """
        if self.exporter is None:
            return
        self.exporter.export(self.records)
