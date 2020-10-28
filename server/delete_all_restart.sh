rm -rf db/
rm log_val_id
rm log_var_id
rm static/uploads/*
export FLASK_APP=server.py
flask run --host 0.0.0.0 --port 8080
