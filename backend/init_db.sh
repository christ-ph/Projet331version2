

 migration="migrations"

 if test -d "$migration"; then
   echo "Le dossier de migration existe."
    rm -rf "$migration"
    echo "Le dossier de migration a été supprimé."
    python3 -m venv steve
    source steve/bin/activate
    pip install -r requirements.txt
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    echo "La base de données a été initialisée et migrée avec succès."
    flask run
 else
    echo "Commencement de l'initialisation de la base de données."
    python3 -m venv steve
    source steve/bin/activate
    pip install -r requirements.txt
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    echo "La base de données a été initialisée et migrée avec succès."
    flask run
 fi