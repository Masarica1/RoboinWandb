echo "./.venv is activated."
source ./.venv/bin/activate

echo "main function is started"
python main.py "$@"

deactivate