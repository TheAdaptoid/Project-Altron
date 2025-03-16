sudo apt install python3 python3-pip python3-venv

python3 -m venv .venv --clear

source .venv/bin/activate

pip install -U -r requirements.txt
pip install -U -r requirements-dev.txt

clear

echo "Setup Complete"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload