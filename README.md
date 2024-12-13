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
    "post_permissions": "public"
}

and click on post (the allowed permissions for the post are: "public", "authenticated", "author", "team")

![imagen](https://github.com/user-attachments/assets/e9043d26-ff9e-49fc-a9c3-6b156e9f4522)



### LIST ALL THE POSTS ON THE BLOG 
to see all the posts published on the blog for which you have acces go to the url 

http://127.0.0.1:8000/api/posts


![imagen](https://github.com/user-attachments/assets/81e6f709-6df4-4fed-a435-cc8078c78e4b)



### MODIFY A POST

if you want to modify a post you created or a post a member of your team created go to the url

http://127.0.0.1:8000/api/posts/id_post and click on patch

![imagen](https://github.com/user-attachments/assets/25d4bacf-7161-4139-96e1-a0498e47113d)

### DELETE A POST

To delete a post you need to be the author, belong to the same team as the auhor or be a superuser. Go to the following url

http://127.0.0.1:8000/api/posts/id_post

and click on the delete botton

![imagen](https://github.com/user-attachments/assets/3990ec2b-8a5a-4cf2-b4ea-f20946001855)



## COMMENTS
To be allowed to comment on a post you need you need to be autheticated as a user

### LIST ALL THE COMMENTS ON A SPECIFIC POST

To know what are the comments on a specific post, go to the url

http://127.0.0.1:8000/api/comments/id_post

![imagen](https://github.com/user-attachments/assets/0c8c9654-d0f9-4074-a2f3-3a8386dd35f9)


### COMMENT ON A POST

To comment on a post go to the url 

http://127.0.0.1:8000/api/comments/id_post

leave a comment in a Json format and click on post

![imagen](https://github.com/user-attachments/assets/cf8b99c2-a4f3-423b-adde-4e1aaade6812)


### DELETE THE COMMENT ON A POST

to delete a comment that you or a memeber of your team did, go to 

http://127.0.0.1:8000/api/comments/delete/comment_id

and click on delete

![imagen](https://github.com/user-attachments/assets/bc580690-ad42-4dc8-a7d5-62c67e22c42c)


## LIKES
To be allowed to like on a post you need to be autheticated as a user

### LIST ALL THE LIKES ON A SPECIFIC POST
In order to know all the likes associated with a specific post go to the url

http://127.0.0.1:8000/api/likes/post_id

![imagen](https://github.com/user-attachments/assets/789086dc-26b2-4b74-bc3b-f1fc0ccd6882)



### LIKE ON A POST



### DISLIKE ON A POST




