venv_name=venv

virtualenv --always-copy -p python3 $venv_name
source $venv_name/bin/activate
pip install -r requirements.txt