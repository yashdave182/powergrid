@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
echo Backend setup complete!
echo Update .env file with your configuration
echo Run: uvicorn app.main:app --reload