# mips
Compile custom language into MIPS Assembly code through Python.

This project can run standalone in Python. The web code was added later to allow others to see the compilation in action on the web rather than through their own Python server.

The python code was created in collaboration with Robert Smayda and Miami University as a part of a college course in 2014.

The basic architecture outlaid here is that:
 - A web activity is launched and uses Ace to create two side-by-side IDEs.
 - A programmer can study the grammar of the language at the top of the website and write code in the newly defined language.
 - Once the user hits the compile button, we send a POST request to the server, which launches our compile.py script on the user's code.
 - If compile.py returns an error we display the compile error in the web browser and if there is no error, we display the MIPS assembly that was compiled by our python code. 

Check out a demo at [my website](http://www.taylorchasewhite.com/mips/).
