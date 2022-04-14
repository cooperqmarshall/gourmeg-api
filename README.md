# Gourmeg UI
Back-end for [gourmeg.org](https://gourmeg.org). Built with python using the flask and Sqlalchemy pachages.

Checkout the accompanying [UI repositury](https://github.com/cooperqmarshall/gourmeg-ui)

## Install
1. Install package dependencies

		pipenv install

2. Create postgres database `recipe-app` (automation coming soon)
3. Configure `.env` file to point to database with included password and postgresql URL
> Optional: set secret string
4. Run database migration

		pipenv run flask db upgrade

5. Run flask

		pipenv run flask run
