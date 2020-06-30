import time
import logging
import functools


# timer decorator
def timer(func):
    @functools.wraps(func) # Without the use of this decorator factory, the name of the example function would have been 'wrapper', 
                           # and the docstring of the original example() would have been lost.
    def wrapper(*args, **kwargs):
        tic = time.perf_counter()
        result = func(*args, **kwargs)
        diff =  time.perf_counter() - tic
        print(f'Function {func.__name__} executed in {diff} seconds')
        return result
    return wrapper

# logger decorator
def logger(func):
    """Log the function signature and return value"""

    logging.basicConfig(filename=f'./logging/{func.__name__}.log', level=logging.INFO)
    @functools.wraps(func)
    def wrapper_logger(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        value = func(*args, **kwargs)
        logging.info(f'Calling {func.__name__!r} with input: {signature} \n Resulted output: {value!r}')
        return value
    return wrapper_logger

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
        print(f"{func.__name__!r} returned {result!r}")           # 4
        return result
    return wrapper_debug

