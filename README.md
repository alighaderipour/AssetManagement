# Asset Manager
simple django vue + Django project

## Installation For Nasser
# 1- Inside Mysql 
create database assetmanagement  
use assetmanagement

# 2-Inside Root Project
### <span style="color:red">backend</span>
/cd backend  
python -m venv venv  
venv/Scripts/Activate  
pip install -r requirements.txt

python manage.py startapp assetmanagement  
python manage.py makemigrations  
python manage.py migrate  
python manage.py create_initial_data.py  
python manage.py


### <span style="color:red">frontend</span>
cd frontend  
npm install  
npm install vue-router@4  
npm install moment-jalaali  
npm install vue3-persian-datetime-picker  
npm run dev


# 3-Login Username & Password
admin
admin123

------------------------------------------------
------------------------------------------------
# ignore below
------------------------------------------------
------------------------------------------------
## Installation For Ali
### backend
mkdir backend
create requirements.txt
python -m venv venv
venv/Scripts/Activate
pip install -r requirements.txt
django-admin startproject config .
python manage.py startapp assetmanagement
python manage.py makemigrations
python manage.py migrate
python manage.py runserver


### frontend
npm create vue@latest
name project frontend
cd .\frontend\
npm install
npm install vue-router@4
npm install moment-jalaali
npm install vue3-persian-datetime-picker
npm run dev