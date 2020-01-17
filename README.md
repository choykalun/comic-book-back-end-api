# comic-book-back-end-api
My final year project for the Bsc Computer Science degree

## Introduction

This is a project that includes creating an API server to 
catalogue comic books online. In order to achieve this, a 
strong knowledge of how to create a server is needed. For
this project, I have decided to use python for implementation
and I will also try to use HTTP/3 request as opposed to HTTP/2
to see how difficult it is to create a server as such. The 
QUIC protocol was introduced in 2012 and announced publicly in 2013.
QUIC is a new transport protocol for the internet, developed by Google.
QUIC (Quick UDP Internet Connections) is 
very similar to TCP + TLS + HTTP2, but implemented on top of UDP.


## Implementation Idea
I will be using python for this project
I would like to see if I can use a microframework for this project.
I have found a useful library for QUIC protocol implementation.
Had done some research on using Hypercorn, however I don't understand why I could not get the latest version on my ubuntu
The latest version I have is 0.5.4 and the latest version that has --quic-bind is 0.9
the above problem was fixed when i upgraded my python version to 3.7 from 3.6
asgi vs wsgi, what is the difference?
Asynchronous Server Gateway Interface vs Web Server Gateway Interface