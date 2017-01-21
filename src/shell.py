from cmd import Cmd

class MyPrompt(Cmd):
    
    def do_greet(self, args):
        """Says hello. If you provide a name, it will greet you with it"""
        if len(args) is 0:
            name = 'User'
        else:
            name = args
        print "Hello, %s" % name
        
    def do_quit(self, args):
        """Quits the program"""
        print "Goodbye"
        raise SystemExit
    
if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = 'azure> '
    prompt.cmdloop('Prompting...')
    