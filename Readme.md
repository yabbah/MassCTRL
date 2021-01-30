# MassCTRL

MassCTRL is a control center for your linux clients and servers. With MassCTRL it's possible to manage updates and other tasks on groups of linux clients or servers. The response of the processes can be logged and reviewed in one single location.  

MassCTRL can also be used as en execution server and centralize all automatic timebased jobs from one crontab instead of setting cronjobs locally on servers.

MassCTRL uses so called group files and recipe files. A recipe can contain one or many ingredients to process during execution. The execution is targeted on a group file containing the clients or servers.

Execution of MassCTRL requires two inputs, group and recipe. Example:  
~~~
py MassCTRL.py group=allservers recipe=status
~~~

It is also possible to use multiple groups and multiple recipes in the same execution. Specify multiple groups or/and recipes separated by ' , '. Example:  
~~~
py MassCTRL.py group=archclients,fileservers recipe=cleanup_tmp,install_new_software
~~~

This system is heavily dependent on ssh and scp and that your enviorment is set up properly for ssh and scp operations. If ssh and scp does not work in your enviorment, MassCTRL will fail too.

### Installation:  
**Requirements:**  
Python 3  
Python module: Blessed  
Python module: Spur  
ssh  
scp  
    
Make sure you have ssh and scp and python3 installed on your system.
clone the MassCTRL repository with the command:  
~~~ 
git clone https://github.com/hum4nizer/MassCTRL
~~~ 
Install required external python modules:  
~~~ 
pip install -r ./requirements.txt
~~~ 

Read this manual and create a group file and a simple recipe. Read and edit the settings file to your needs and correct all paths to match your system. Next **create a keyfile** with the credentials to your clients and servers.  

Do a test run with a non destructive command in the recipe like uname och uptime. Most information is in this manual. If there is any questions about operation, bugs, feature requests, please contact med through the discussion board on Github.

### Group file and syntax:

Each group file contains one or more clients to build the specific group. The syntax of the group file is simple and as follows. Clientname IP-address Ex:
~~~
clab-pc01 192.168.4.10  
clab-pc02 192.168.4.11  
clab-pc03 192.168.4.12  
clab-pc04 192.168.4.13  
clab-pc05 192.168.4.14  
~~~
Space is the delimiter when reading files and all words in all files are separated by a space and nothing else (like Tab).

The option of exluding a client is supported by putting a ' # ' as the first character of the line.


### Recipe file and syntax:
Each ingredient in a recipe starts with a command followed by a ' : '. Valid commands are:  
**EXEC** - Executes remote command  
**LOCAL** - Executes local command  
**PUT** - Sends a file to remote client  
**GET** - Retrieves file from remote client  

You can also comment out an ingredient by putting a ' # ' as the first character of the line.  

An example of a multi command recipe could be:  
~~~
LOCAL:mkdir /home/master/tmplogs/  
GET:/var/log/software.log /home/master/tmplogs/  
EXEC:mkdir /tmp/lab/  
PUT:/home/master/Download/some_script.py /tmp/lab/  
EXEC:python3 /tmp/some_script.py  
EXEC:rm /tmp/lab/some_script.py  
~~~

**Line 1** creates a directory on the local machine for saving all the logs into from the remote machines.  
**Line 2** retrieves the log file software.log from all machines in the group file and saves them to the newly created local directory /home/master/tmplogs  
**Line 3** creates a directory named /tmp/lab on the remote clients  
**Line 4** sends a script called some_script to the remote clients and saves it in the directory called /tmp/lab  
**Line 5** executes the uploaded script 'some_script.py' from the driectory /tmp  
**Line 6** removes the executed script  

### Built-in recipes:  
**list** - lists all groups and recipes in your system. Example:  
~~~
py MassCTRL.py group=clab recipe=list  
~~~
Or directly:  
~~~
py MassCTRL.py list  
~~~

**status** - Show status on selected group  
Status is monitoring the specified group continous until stopped. Example:  
~~~
py massCTRL.py group=clab recipe=status  
~~~

### Key file

> **_ATTENTION!_** **Always remember to set your key file permissions to only read/writable for the user that will execute MassCTRL!** Command: 
> ~~~
> chmod 600 keyfile.dat
> ~~~  

This file contains credentials to all clients and servers. If the enviorment is set up with a password-less login to servers and clients, MassCTRL will only use the username from that file. If your enviorment is set up for user and password login it will use those values from this file.

You also have an option to use a master accout if that is the way your envoirment is setup. That means that all clients and servers have a identical account for login. To enable master account login, use the word masteraccount as the client name in the first line og the key file (see example).

The syntax of the key file is: Clientname IP-Address Username Password  
As in all files, the values should be separated by a space and nothing else.

**Example of a key file for username and password login where :**  
~~~
clab-pc01 192.168.4.10 admin EY!R3Uyr24  
clab-pc02 192.168.4.11 superuser freIJER23j  
clab-pc03 192.168.4.12 chayene SJeif3jf&e  
clab-pc04 192.168.4.12 admin eJert3jfr#
~~~

**Example of keyfile where a master account is used:**  
~~~
masteraccount 0.0.0.0 masteruser HUW2e&heuE8HJh!!jew=
~~~

If you only use host lookup with DNS or hosts-file and you have dynamic IP-addresses assignes to the clients with a DHCP server you just set the IP-address to 0.0.0.0 and set the use_hostname option to **True** in the settings file.  

**Example of a key file in an enviorment with DHCP and hostname lookup:**  
~~~
clab-pc01 0.0.0.0 admin EY!R3Uyr24  
clab-pc02 0.0.0.0 superuser freIJER23j  
clab-pc03 0.0.0.0 chayene SJeif3jf&e  
clab-pc04 0.0.0.0 admin eJert3jfr#
~~~

An enviorment that is set up with a working certificate login without password the option ' private_key_login ' should be set to **True** in the settings file.

**Example file for an enviorment with passwordless login and DHCP:**  
~~~
clab-pc01 0.0.0.0 admin -  
clab-pc02 0.0.0.0 superuser -  
clab-pc03 0.0.0.0 chayene -  
clab-pc04 0.0.0.0 admin -
~~~

### Log files
There are two options to log operation. Log options can be defined in the settings file and are named  write_master_log and write_client_log. Both options take True or False. You can write both typ of logs simultaneously. write_master_log option logs all operation to one file. write_client_log option logs all operation to a specific file per client.

### Settings file
The settings file are pre-defined with example values. All values are user changable to make MassCTRL fit your enviorment and needs. All settings is explained in the settings file and should be reviewed before execution of MassCTRL to make all options fit your enviorment and needs.

### Examples
Lets say you have a classroom with 25 linux clients and you need to install a new software package in .deb format. Just make a recipe for the install and execute it on the group file conyaining the classroom clients. Ex.

**group file (clab):**  
~~~
clab-pc01 192.168.4.10  
clab-pc02 192.168.4.11  
clab-pc03 192.168.4.12  
clab-pc04 192.168.4.13  
clab-pc05 192.168.4.14  
~~~
and so on.....

**recipe file (install_new_sw):**  
~~~
PUT:/home/master/Download/new_software.deb /tmp/  
EXEC:sudo dpkg -i /tmp/new_software.deb  
EXEC:rm /tmp/new_software.deb
~~~

To install the new software on to all clients in the class room, execute command:  
~~~
py MassCTRL.py group=clab recipe=install_new_sw
~~~


