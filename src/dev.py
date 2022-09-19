import json
import lambda_function


def dev():
	test_event = {
		'dry_run': True
	}
	return lambda_function.lambda_handler(event=test_event, context={})


if __name__ == '__main__':
	print(json.dumps(dev()))
