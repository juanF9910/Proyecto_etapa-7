# Proyecto_etapa-7
The objective of this app is to allow users to create posts on a blog, and interact with others posts leaving likes and comments. According to the posts permissions which are public, authenticated, author or team. 

##CLONE THE REPO
In order to clone this repo you should go to your terminal and execute the following: 

git clone: git@github.com:juanF9910/Proyecto_etapa-7.git

##SETTLELING THE ENVIROMENT

after cloning the repo, create a virtual enviroment into the directory of the proyect

python -m venv env 

the enviroment is created already, now we need to activate it 

source env/bin/activate

In order to install all the needed libraries in the enviroment execute

pip install -r requirements.txt

Now everything is ready to work

## USERS

###CREATE A SUPERUSER

To manage the user creation first we need to start by creating a superuser. Go to

Proyect_etapa-7/avanzablog and execute

python manage.py createsuperuser 

follow the steps to stablish the name, password. To log in as a superuser, run in the console the following

python manage.py runserver 

you will see this


![imagen](https://github.com/user-attachments/assets/22d8eb44-1044-4163-b883-22996d56fa6e)


then just execute ctrl+click on http://127.0.0.1:8000/ 

### CREATE A USER

### ASSIGN USERS TO THE GROUPS 

## GROUPS 

the group creation is managed by the default Djando Rest Framework, in order to create a group you need to be a super user.



### CREATE A GROUP



## POSTS

### LIST ALL THE POSTS ON THE BLOG 

### CREATE A POST

### MODIFY A POST

### DELETE A POST



## COMMENTS

### LIST ALL THE COMMENTS ON A SPECIFIC POST

### COMMENT ON A POST

### DELETE THE COMMENT ON A POST


## LIKES


### LIST ALL THE LIKES ON A SPECIFIC POST

### LIKE ON A POST

### DISLIKE ON A POST




