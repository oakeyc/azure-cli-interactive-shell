import cmd
from clint.textui import puts, indent, colored

class AzureShell(cmd.Cmd):
    puts(colored.cyan("Welcome to Azure\n", bold=True))
    prompt = 'azure>> '
    file = None
    
    def do_quit(self, arg):
        'Quit the program'
        print("Quiting, you quiter")
        quit()
    
    def do_things(self, arg):
        'Does things'
        print("Doing things")
        puts(colored.cyan("And now in cyan"))
        
if __name__ == '__main__':
    AzureShell().cmdloop()