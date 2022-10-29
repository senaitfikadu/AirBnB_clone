#!/usr/bin/python3
'''Method Command Interpreter'''
import cmd
import shlex
import models
from datetime import datetime
from models.base_model import BaseModel
from models import storage
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review
import re
from shlex import split

def parse(arg):
    curly_braces = re.search(r"\{(.*?)\}", arg)
    brackets = re.search(r"\[(.*?)\]", arg)
    if curly_braces is None:
        if brackets is None:
            return [i.strip(",") for i in split(arg)]
        else:
            lexer = split(arg[:brackets.span()[0]])
            retl = [i.strip(",") for i in lexer]
            retl.append(brackets.group())
            return retl
    else:
        lexer = split(arg[:curly_braces.span()[0]])
        retl = [i.strip(",") for i in lexer]
        retl.append(curly_braces.group())
        return retl

        
class HBNBCommand(cmd.Cmd):
    prompt = '(hbnb) '
    __classes = {
        "BaseModel",
        "User",
        "State",
        "City",
        "Place",
        "Amenity",
        "Review"
    }

    def do_create(self, args):
        '''Create a new instance of BaseModel, save it and prints the id
           Usage: create <class name>
        '''
        args = args.split()
        if len(args) == 0:
            print("** class name missing **")
        elif args[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            new_creation = eval(args[0] + '()')
            models.storage.save()
            print(new_creation.id)

    def do_show(self, args):
        '''Prints the string representation of a specific instance
           Usage: show <class name> <id>
        '''
        strings = args.split()
        if len(strings) == 0:
            print("** class name missing **")
        elif strings[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(strings) == 1:
            print("** instance id missing **")
        else:
            obj = models.storage.all()
            key_value = strings[0] + '.' + strings[1]
            if key_value in obj:
                print(obj[key_value])
            else:
                print("** no instance found **")

    def do_destroy(self, args):
        '''Delete an instance
           Usage: destroy <class name> <id>
        '''
        args = args.split()
        objects = models.storage.all()

        if len(args) == 0:
            print('** class name missing **')
        elif args[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(args) == 1:
            print('** instance id missing **')
        else:
            key_find = args[0] + '.' + args[1]
            if key_find in objects.keys():
                objects.pop(key_find, None)
                models.storage.save()
            else:
                print('** no instance found **')

    def do_all(self, args):
        '''Print a string representation of all instances
           Usage: all <class name>
        '''
        args = args.split()
        objects = models.storage.all()
        new_list = []

        if len(args) == 0:
            for obj in objects.values():
                new_list.append(obj.__str__())
            print(new_list)
        elif args[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            for obj in objects.values():
                if obj.__class__.__name__ == args[0]:
                    new_list.append(obj.__str__())
            print(new_list)

    def do_update(self, line):
        """Updates an instance based on the class name and id
        by adding or updating attribute.
        """
        args = shlex.split(line)
        args_size = len(args)
        if args_size == 0:
            print('** class name missing **')
        elif args[0] not in self.allowed_classes:
            print("** class doesn't exist **")
        elif args_size == 1:
            print('** instance id missing **')
        else:
            key = args[0] + '.' + args[1]
            inst_data = models.storage.all().get(key)
            if inst_data is None:
                print('** no instance found **')
            elif args_size == 2:
                print('** attribute name missing **')
            elif args_size == 3:
                print('** value missing **')
            else:
                args[3] = self.analyze_parameter_value(args[3])
                setattr(inst_data, args[2], args[3])
                setattr(inst_data, 'updated_at', datetime.now())
                models.storage.save()
                
    def check_class_name(self, name=""):
        """Check if stdin user typed class name and id."""
        if len(name) == 0:
            print("** class name missing **")
            return False
        else:
            return True

    def check_class_id(self, name=""):
        """Check class id"""
        if len(name.split(' ')) == 1:
            print("** instance id missing **")
            return False
        else:
            return True

    def found_class_name(self, name=""):
        """Find the name class."""
        if self.check_class_name(name):
            args = shlex.split(name)
            if args[0] in HBNBCommand.__classes:
                if self.check_class_id(name):
                    key = args[0] + '.' + args[1]
                    return key
                else:
                    print("** class doesn't exist **")
                    return None

    def do_quit(self, args):
        '''<Quit> Command To Exit The Program'''
        return True

    def do_EOF(self, args):
        '''Handles end of file'''
        return True

    def emptyline(self):
        '''dont execute anything when user
           press enter an empty line
        '''
        pass
    def do_count(self, arg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        argl = parse(arg)
        count = 0
        for obj in storage.all().values():
            if argl[0] == obj.__class__.__name__:
                count += 1
        print(count)

    def default(self, arg):
        """Default behavior for cmd module when input is invalid"""
        argdict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }
        match = re.search(r"\.", arg)
        if match is not None:
            argl = [arg[:match.span()[0]], arg[match.span()[1]:]]
            match = re.search(r"\((.*?)\)", argl[1])
            if match is not None:
                command = [argl[1][:match.span()[0]], match.group()[1:-1]]
                if command[0] in argdict.keys():
                    call = "{} {}".format(argl[0], command[1])
                    return argdict[command[0]](call)
        print("*** Unknown syntax: {}".format(arg))
        return False

if __name__ == '__main__':
    HBNBCommand().cmdloop()
