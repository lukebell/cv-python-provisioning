#!/usr/bin/env bash
#!/usr/bin/python

# activates virtual environment
. cv-env/bin/activate

# download dependencies
pip install -r requirements.txt

# run process
python app.py