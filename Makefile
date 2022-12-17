test:
	pipenv run python -m pytest -W ignore::DeprecationWarning -o log_cli=true -o log_cli_level="DEBUG"
