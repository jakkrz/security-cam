# security-cam

A security camera script written in Python. Uses OpenCV to detect faces and then begins recording, sending the video file using TCP sockets to the server once it is done recording.

# How to Set it Up

The *server.py* file should go on the computer that is the server and will be receiving the files. *networking.py* and *main.py* go onto the client, i.e. the device recording and sending the files. Set the `HOST-NAME` variable in *networking.py* to the host-name of the server. When ready, run *server.py* on the server and subsequently run the *main.py* file on the client.

If everything goes to plan, the sockets should establish a connection. 

Please note that you need to connect a camera to the client. (duh!)
