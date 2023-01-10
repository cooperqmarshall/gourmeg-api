test:
	pipenv run python -m pytest -W ignore::DeprecationWarning -o log_cli=true -o log_cli_level="DEBUG"
server:
	pipenv run gunicorn app:recipe_app
devserver:
	pipenv run flask run
