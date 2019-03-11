from prompt_toolkit import prompt, PromptSession
from seiyuu import *

commands = { 'quit':'quit'
           , 'exit':'quit'
           , 'help':'help'
           , 'search':'search'
           , 'find':'search'
           , 'lookup':'search'
           }

desc = { 'quit':["terminates a CLI session"]
       , 'help':[ "displays a list of available commands"
                , "prints usage information for"
                ]
       }


comlist = commands.keys()

def alias(arg):
    if arg in set(commands.values()):
        return ""
    elif arg in comlist:
        return ("[alias for: %s] " % commands[arg])
    else:
        return "?"

def do_quit(cmd, arg):
    if len(arg) == 0:
        return 0
    else:
        print("[%s] expected no arguments, but found '%s'" % (cmd, arg))
        return 1

# verbose option: list command aliases in help dialog
DISPLAY_ALIASES = False

def do_help(cmd, arg):
    if len(arg) == 0:
        if DISPLAY_ALIASES:
            print ("supported commands: " + ', '.join(set(commands.keys())))
        else:
            print ("supported commands: " + ', '.join(set(commands.values())))
        return 0
    if arg in commands:
        trans = commands[arg]
        for i in range(len(desc[trans])):
            print ("[%s] %s%s: %s%s" % (cmd, arg, "".join([" <arg>"]*i), alias(arg), desc[trans][i]+("".join([" <arg>"]*i))))
        return 0
        #print("[help] help: displays a list of available commands")
        #print("[help] help <cmd>: prints usage information for <cmd>")
        return 0
    else:
        print("[help] no such command '%s'" % arg)
        return 1


def parse_cmd(s):
    (cmd, sp, arg) = s.partition(" ")
    return cmd, arg.strip()


def main(session):
    while True:
        try:
            resp = session.prompt("seiyuu> ")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            if len(resp) == 0:
                continue
            cmd, arg = parse_cmd(resp)
            if cmd in commands:
                trans = commands[cmd]
            if trans == "quit":
                v = do_quit(cmd, arg)
                if v == 0:
                    break
                continue
            elif trans == "help":
                do_help(cmd, arg)
                continue
            else:
                print("command '%s' not currently supported" % cmd)


if __name__ == '__main__':
    session = PromptSession()
    main(session)
