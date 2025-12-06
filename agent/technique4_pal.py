import re
import signal
from api import call_model_chat_completions

# Whitelisted builtins available inside the PAL sandbox. The model's generated
# code can use these; everything else (open, eval, exec, __import__ of arbitrary
# modules, etc.) stays unavailable.
_SAFE_BUILTINS = {
    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
    "len": len, "range": range, "int": int, "float": float, "pow": pow,
    "divmod": divmod, "sorted": sorted, "reversed": reversed,
    "list": list, "tuple": tuple, "set": set, "dict": dict,
    "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
    "all": all, "any": any, "str": str, "bool": bool,
}

# Pure-computation modules PAL is allowed to import.
_ALLOWED_MODULES = {"math", "fractions", "statistics", "itertools", "decimal"}


def _safe_import(name, *args, **kwargs):
    if name.split(".")[0] in _ALLOWED_MODULES:
        return __import__(name, *args, **kwargs)
    raise ImportError(f"import of '{name}' is not allowed in PAL sandbox")


class _Timeout(Exception):
    pass


def _alarm_handler(signum, frame):
    raise _Timeout()


def pal_solve(problem, time_limit=5):
    system = """You are a helpful assistant. For math problems, write Python code to solve it.
Put the final answer in a variable called 'answer'.
You may use the math module. Only output the Python code, nothing else. No markdown, no explanation."""

    result = call_model_chat_completions(problem, system=system, temperature=0.0)

    if not result["ok"] or not result["text"]:
        return {"answer": "", "confidence": 0.0}

    code = result["text"].strip()
    code = re.sub(r'^```python\s*', '', code)
    code = re.sub(r'^```\s*', '', code)
    code = re.sub(r'\s*```$', '', code)

    # Reject runaway or unbounded code. `while` is the main infinite-loop risk;
    # `for` loops are allowed but still bounded by the wall-clock timeout below.
    if len(code) > 800 or 'while ' in code:
        return {"answer": "", "confidence": 0.0}

    safe_globals = {"__builtins__": {**_SAFE_BUILTINS, "__import__": _safe_import}}
    local_vars = {}

    # Guard against long-running code with a wall-clock timeout (Unix main thread).
    alarm_set = False
    old_handler = None
    if hasattr(signal, "SIGALRM"):
        try:
            old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
            signal.alarm(time_limit)
            alarm_set = True
        except (ValueError, OSError):
            alarm_set = False

    try:
        exec(code, safe_globals, local_vars)
        answer = local_vars.get("answer", "")
        if answer != "":
            return {"answer": str(answer), "confidence": 0.95}
    except Exception:
        pass
    finally:
        if alarm_set:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    return {"answer": "", "confidence": 0.0}
