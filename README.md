lesstrouble.py
-----------
Trying to find a working *less* monitor/generator appeared to be a difficult
mission. I tried a few, but they either crashed or failed to include
dependencies, or just gave weird errors.

So, I gave in and created my own, in Python. **lesstrouble.py** is a very simple
LESS monitor. It generates the CSS with your installed and hopefully preferred 
version of the `lessc` compiler. It's a robust tool with no fancy features.
Except some odd term colors :)

**lesstrouble.py will do these things:** 
* Reads a master LESS file, and includes all its dependencies and their dependencies and so on.
* It checks for changes in all the associated files.
* When a change is noticed, it will run the `lessc` compiler and return monitoring changes.
* Keeps running in the background and you won't have any concerns about compiling. 
But keep an eye out for syntax errors.

**lesstrouble.py won't do these things:**
* Write your less files.
* Clean your house.
* Your tax declaration.

Installation
------------
For lesstrouble.py to work, you need:
* A less compiler called `lessc` installed globally and in the path.
* Python (duh) (not tested with Python 3)
* A Unix shell (will probably not work in Windows, MacOSX maybe?)

Copy lesstrouble.py in either /usr/local/bin or your ~/bin
and make sure it's marked as executable `chmod +x lesstrouble.py`

If your Python binary is installed anywhere than /usr/bin, edit the
first line of the script and change it to your Python binary. 

Usage
-----
lesstrouble.py is simple to use. Please note that it won't compile
any CSS until a change has been made.

`lesstrouble.py [options] lessfile.less [output CSS file]`

*If no output file is specified it will end up in the working directory.*

**Options**
 -c     Is the only available option, and it will compress the CSS.
