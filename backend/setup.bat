<<<<<<< HEAD
@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
echo Backend setup complete!
echo Update .env file with your configuration
=======
@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
echo Backend setup complete!
echo Update .env file with your configuration
>>>>>>> 362b52b683dacbc43ff77fceb651bab6d409b1b0
echo Run: uvicorn app.main:app --reload