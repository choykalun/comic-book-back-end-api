# comic-book-back-end-api


## Introduction

This is a project that includes creating an API server to 
catalogue comic books online. The technologies used are Quart and Hypercorn.
In this readme file, you will find how to use the API server and what the url routes are.


## Pre-equisites

The server can only be installed in Ubuntu at the moment.
Python 3.7 or higher is required for the operating system.


## How to set up the environment?

First you need to clone the repository from github.
1. ```git clone https://www.github.com/choykalun/comic-book-back-end-api```
2. ```cd comic-book-back-end-api/src```
3. ```pip3 install -r requirements.txt```
These three commands should set up the environment if the pre-equisites are met. 

## Creating the database

In order to create the database, there is a schema.sql file that should be part of the git clone.
There are a few steps to create the database:
1. ```export QUART_APP=run:app```
2. ```quart init_db```
3. check if the database has been created with the command above using ```ls```


## Usage

### /user

This route is used for registering a user only.
This route accepts POST and DELETE as a method. 

#### POST
You must supply a JSON body in the request to register a user.
The JSON body should contain the following fields :
```
{
		"email" : your email (must be unique),
		"firstname" : your first name,
		"lastname" : your last name,
		"username" : username (must be unique),
		"password" : password
}
```

The response returned should contain a success message and a 201 response code.


#### DELETE
For the DELETE method, you must supply the token in the authentication header to delete your own account.
The server will respond with a 200 code if successful and a message to acknowledge the deletion.

### /login

This route is used to login users only and the route only accepts POST as a method.
You must supply the credentials in the query parameters.

```
{
	"username" : "",
	"password" : ""
}
```

The response returned should contain a success message with a token and a 200 response code

The response message will contain something similar like :
```
{
	"token" : ""
}
```

### /comic/issue

This route is used when the information of comic book issues is needed. This route returns a list of comic book issues after supplying the name of the issue and the issue number. The method used here is GET. You must supply the access token in the authentication header for this route.
Supply the information in the JSON body like the format below :

```
{
	"issue" : 
	{
		"name" : "",
		"issue_number" : ""
	}
}
```

The response returned should contain a list and the response code is 200.
The response message looks like the following :
```
{
	"result" : 
	{
		list_of_issues : [
			{JSON Object},
			{JSON Object}
		]
	}
}
```


### /comic/issue/<issueid>

This route is used for the issue. There are two methods for this route, POST and GET.

#### POST
This method is to add a comic issue under the users account. You must supply the access token in the request header to gain access to this route. 

The request does not need any content in the body. The response should return a message for success and a 201 response code

#### GET
This method will return the comic issue information back to the user if they already have stored in their account. You must supply the access token in the request header to gain access to this route.

The request does not need any content in the body. The response should return a JSON body with the comic issue information and a response code of 200.

#### DELETE
This method is used to delete the issue under the users account. This will not delete the issue entry in the database. You must also supply the access token in the request header to gain access to this route.

The response will return a successful message along with the response code 200.


### /comic/volume

This route is used when the information of comic book volumes is needed. This route returns a list of comic book volumes after supplying the name of the volume and the number of issues in the volume. The method used here is GET. You must supply the access token in the authentication header for this route.
Supply the information in the JSON body like the format below :

```
{
	"volume" : 
	{
		"name" : "",
		"count_of_issues" : ""
	}
}
```

The response returned should contain a list and the response code is 200.
The response message looks like the following :
```
{
	"result" : 
	{
		list_of_volumes : [
			{JSON Object},
			{JSON Object}
		]
	}
}
```


### /comic/volume/<volumeid>

This route is used for the volume. There are two methods for this route, POST and GET.

#### POST
This method is to add a comic volume under the users account. You must supply the access token in the request header to gain access to this route. 

The request does not need any content in the body. The response should return a message for success and a 201 response code

#### GET
This method will return the comic volume information back to the user if they already have stored in their account. You must supply the access token in the request header to gain access to this route.

The request does not need any content in the body. The response should return a JSON body with the comic volume information and a response code of 200.

#### DELETE
This method is used to delete the volume under the users account. This will not delete the volume entry in the database. You must also supply the access token in the request header to gain access to this route.

The response will return a successful message along with the response code 200.


### /comics/issues

This route is used to list all the issues that belong to the user. There must be an access token in the request header to use this route. This route only has one method, GET. There are 2 query params that can be added to change the list of returned items.

Query Params :
| filter | field : value |
| sort | field_desc/asc |

e.g. ```{"filter" : "name:Spider-man"}``` this will return all the issues containing Spider-man in its name.

The response returned will contain a list of issues and a response code of 200 if success.

```
{
	list_of_issues : [
		{JSON Object}
	]
}
```


### /comics/volumes

This route is used to list all the volumes that belong to the user. There must be an access token in the request header to use this route. This route only has one method, GET. There are 2 query params that can be added to change the list of returned items.

Query Params :
| filter | field : value |
| sort | field_desc/asc |

e.g. ```{"filter" : "name:Spider-man"}``` this will return all the volumes containing Spider-man in its name.

The response returned will contain a list of volumes and a response code of 200 if success.

```
{
	list_of_volumes : [
		{JSON Object}
	]
}
```


### /manga/volume

This route is used to create a manga volume for the user. This route must be accessed by providing an access token, otherwise you won't be able to use it. To create a new manga volume, there are some information that must be submitted. They must be submitted in the JSON body of the request. The request must use the `POST` method

```
{
	"manga" : 
	{
		"name" : "",
		"publisher" : "",
		"author" : "",
		"illustrator" : "",
		"volumenumber" : ""
	}
}
```

The response will return a message and a response code.


### /manga/volumes

This route is used to list all the manga volumes users have stored under their account. This route must be accessed by providing an access token. This route only accept the `GET` method. Like the other list routes, this route can also have query parameters to control what items are returned to the list.

Query Params :
| filter | field : value |
| sort | field_desc/asc |

The response returned will contain a list of manga volumes that belongs to the user and a response code.

Sample response : 
```
{
	"list_of_mangas" : 
	[
		{JSON Object}
	]
}
```


### /manga/volume/<manga_id>

This route is used to delete a manga entry for the user. This route can only be accessed by an access token. This route uses the `DELTE` method.

The response returned will contain a message and the response code.



## Below are the table of response codes the server wil return.


| Status Code | Description |
| :--- | :--- |
| 200 | `OK` |
| 201 | `CREATED` |
| 400 | `BAD REQUEST` |
| 404 | `NOT FOUND` |
| 409 | `Already Exists` |
| 500 | `INTERNAL SERVER ERROR` |
