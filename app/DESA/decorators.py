import time
import logging
import functools


# timer decorator
def timeer(func):
    @functools.wraps(func) # Without the use of this decorator factory, the name of the example function would have been 'wrapper', 
                           # and the docstring of the original example() would have been lost.
    def wrapper(*args, **kwargs):
        tic = time.perf_counter()
        result = func(*args, **kwargs)
        diff = tic - time.perf_counter()
        print(f'Function {func.__name__} executed in {diff}')
    return result
return wrapper

# logger decorator
def logger(func):
        logging.basicConfig(filename=f'./logging/{method.__name__}.log', level=logging.INFO)
        
        @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        print(f"{func.__name__!r} returned {value!r}")           # 4
        logging.info(f'Ran with args: {args_repr}, and kwargs {kwargs_repr}')
    return func(*args, **kwargs)
return wrapper


# debugger decorator
def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return result
    return wrapper_debug

    