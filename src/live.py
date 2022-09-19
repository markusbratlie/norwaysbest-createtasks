import json
import lambda_function


def live():
    return lambda_function.lambda_handler(event={}, context={})


if __name__ == '__main__':
    print(json.dumps(live()))
