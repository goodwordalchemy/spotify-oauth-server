ELM_SRC_DIRECTORY="./src"

# build elm files
fswatch -o $ELM_SRC_DIRECTORY | xargs -n1 scripts/build.sh &

# build flask files
export FLASK_DEBUG=1 &&
export FLASK_APP="app.py" &&
flask run
