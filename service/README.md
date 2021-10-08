-- Running Database Migrations --

After a database change run:

  alembic revision --autogenerate -m 

To apply the migration:

  alembic upgrade head
