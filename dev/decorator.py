import traceback

def my_decorator(func):
    def wrapper():
        if not go_nogo():
            print("I am not gonna proceed")
            return
        func()
    return wrapper


def second_decorator(func):
    def wrapper():
        func()
        print("I am executed after func")
    return wrapper


def go_nogo():
    return False

@my_decorator
@second_decorator
def test():
    print("something here")


if __name__ == '__main__':
    try:
        test()
    except Exception as e:
        traceback.print_exc()