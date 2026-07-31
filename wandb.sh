ehco "./.venv is activated."
source ./.venv/bin/activate

ehco "main function is started"
python main.py "$@"

deactivate