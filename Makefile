.PHONY: test

test:
	flake8
	coverage erase
	DJANGO_SETTINGS_MODULE=tests.settings PYTHONPATH=. coverage run `which django-admin.py` test tests
	coverage combine
	coverage html
	coverage report