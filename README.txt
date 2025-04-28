These are pretty straighforward.  The scripts download everything to a dated folder.

Option 1. If you want to use the jupyter notebook you want tk_v1.ipynb.

Option 2. If you want to use a straight python script you want tk_v2.python

Option 3. If you want to try the windows executable I made of this script then download tk_v2.zip, unzip it.  It's a command line tool so you still have to use either cmd or powershell to run it.  

You need your user ID and an active session cookie from tk.

To get user id, go on tk and log in.  Open the inspect window in your browser and go to the console.  Type current_user.  It should show you a user number.  write that down.

Go to the network tab of the inspector in your browser and then reload the tk page.  Scroll up and highlight the first entry.  You should get a pop up that shows you several things.  

You're looking for the session cookie. It's probably labeled 'cookie' and is super long.  It starts with "tavern-keeper:..."

Copy that value and paste it into a text editor.  Then copy the string between the = sign and the first ;.

To run the notebook (option 1), paste both your ID and the cookie value in at the top of the script.  Make sure it has quotes around it. 

to run the stand alone python script or the executable (option 2 or 3) use the command line variables --user_id=(your number) --session_id=(that long cookie string)