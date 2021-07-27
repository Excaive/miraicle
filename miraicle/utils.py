import warnings


def start_log(func):
    def wrapper(*args, **kwargs):
        try:
            print(color(f"method '{func.__name__}' starts", 'green'))
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            print(color(f"method '{func.__name__}' raised an error: {e.__class__.__name__}", 'red'))
            raise e

    return wrapper


def end_log(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print(color(f"method '{func.__name__}' has called", 'green'))
            return result
        except Exception as e:
            print(color(f"method '{func.__name__}' raised an error: {e.__class__.__name__}", 'red'))
            raise e

    return wrapper


def color(string, to_color):
    color_code_dict = {'black': 30,
                       'red': 31,
                       'green': 32,
                       'yellow': 33,
                       'blue': 34,
                       'violet': 35,
                       'cyan': 36,
                       'white': 37}
    color_code = color_code_dict.get(to_color, 30)
    return f'\033[0;{color_code}m{string}\033[0m'


class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            warnings.warn(f'不能为类 {cls.__name__} 创建两个实例')
        return cls.__instances[cls]
