postgres:
	docker run -p 5432:5432 --name postgres-14 -e POSTGRES_PASSWORD=secret -e POSTGRES_USER=root -d postgres:14-alpine

createdb:
	docker exec -it postgres-14 createdb --username=root --owner=root recipe-app

test:
	pipenv run python -m pytest -W ignore::DeprecationWarning -o log_cli=true -o log_cli_level="DEBUG"

server:
	pipenv run gunicorn app:recipe_app

devserver:
	pipenv run flask run
