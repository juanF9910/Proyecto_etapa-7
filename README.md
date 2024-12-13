# Proyecto_etapa-7
The objective of this app is to allow users to create posts on a blog, and interact with others posts leaving likes and comments. According to the posts permissions which are public, authenticated, author or team. 

## CLONE THE REPO
In order to clone this repo you should go to your terminal and execute the following: 

git clone: git@github.com:juanF9910/Proyecto_etapa-7.git

## SETTLELING THE ENVIROMENT

after cloning the repo, create a virtual enviroment into the directory of the proyect

python -m venv env 

the enviroment is created already, now we need to activate it 

source env/bin/activate

In order to install all the needed libraries in the enviroment execute

pip install -r requirements.txt

Now everything is ready to work

## USERS

### CREATE A SUPERUSER

To manage the user creation first we need to start by creating a superuser. Go to

Proyect_etapa-7/avanzablog and execute

python manage.py createsuperuser 

follow the steps to stablish the name, password. To log in as a superuser, run in the console the following

python manage.py runserver 

you will see this


![imagen](https://github.com/user-attachments/assets/22d8eb44-1044-4163-b883-22996d56fa6e)


then just execute ctrl+click on http://127.0.0.1:8000/


To sign in as a super user go to http://127.0.0.1:8000/admin and just put the credentials 

![imagen](https://github.com/user-attachments/assets/38d00ec8-8855-4c3b-8f16-07a61af9a2d1)


### CREATE A USER

to create a user just click on add and stablish the username and the password


![imagen](https://github.com/user-attachments/assets/40b965fa-f8ff-41c5-8ede-495e55eb68a6)


## GROUPS 

### CREATE A GROUP

In the url http://127.0.0.1:8000/admin, click on  add groups, define the name of the group and click on save and continue editing

### ASSIGN USERS TO THE GROUPS 

On a specific user's tab choose the group you want to assign the user and then the rightarrow


![imagen](https://github.com/user-attachments/assets/227d09c6-75b9-4eaf-af1c-5695150817b3)



## POSTS

### CREATE A POST

in order to create a post you need to be loged in as a user

go to the url http://127.0.0.1:8000/api/posts/create/ and create your post with a json format  

{
    "title": "Exploring REST Framework",
    "content": "This post discusses how to use Django REST Framework to build robust APIs effectively.",
    "post_permissions": "public"  // Example values: "public", "authenticated", "author", "team"
}

and click on post

![imagen](https://github.com/user-attachments/assets/e9043d26-ff9e-49fc-a9c3-6b156e9f4522)




### LIST ALL THE POSTS ON THE BLOG 

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




