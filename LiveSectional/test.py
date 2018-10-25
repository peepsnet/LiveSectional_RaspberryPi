#!/usr/bin/env python
import sys

#file = open("test.txt","a") 
#file.write("Hello World\n") 
#file.write("This is our new text file\n") 
#file.write("and this is another line.\n") 
#file.write("Why? Because we can.\n") 
#file.close() 

print(sys.argv)
args = str(sys.argv[1:]).split("','")
print

for arg in sys.argv[1:]:
	print(arg)

print

for arg in args:
	print(arg)
