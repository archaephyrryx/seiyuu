#coding=utf-8
from prompt_toolkit import prompt, PromptSession
from seiyuu import *

modes = [ "search", "graph", "compare", "id", "audit" ]

commands = { 'quit':'quit'
           , 'exit':'quit'
           , 'help':'help'
           , 'mode':'mode'
           , 'search':'search'
           , 'find':'search'
           , 'lookup':'search'
           }

desc = { 'quit':["terminates a CLI session"]
       , 'help':[ "displays a list of available commands"
                , "prints usage information for"
                ]
       , 'mode':[ "display current mode"
                , "switch to mode"
                ]
       , 'search':[ "enters search mode and parses query strings"
                  , "remain in current mode and perform a lookup using keyword"
                  ]
       }


comlist = commands.keys()

def show_env(env):
    print(str(env))

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

def write_registers(vals, env):
    env['registers'].clear()
    for i in range(len(vals)):
        env['registers'][('%'+str(i))] = vals[i]
    return

def do_mode(session, mode, env, current="main"):
    if len(mode) == 0:
        print("[mode]: currently in mode '%s'" % current)
        return 0
    if mode not in modes:
        print ("[mode]: no such mode '%s'" % mode)
        do_help("mode", "mode")
        return 1
    else:
        if mode == "search":
            v = do_query_mode(session, env, compare=False)
            return v
        if mode == "compare":
            v = do_query_mode(session, env, compare=True)
            return v

def pretty_print(anime, caller=""):
    print(caller+"pretty printing not yet implemented ¯\_(ツ)_/¯")
    print(str(anime))
    return

def do_query_mode(session, env, compare=False):
    lcomp = compare
    while True:
        modstr = "*compare" if lcomp else "*search"
        try:
            query = session.prompt(modstr+"> ")
        except KeyboardInterrupt:
            continue
        except EOFError:
            return 0
        else:
            if query[0] == "!":
                esc = query[1:]
                if esc in commands:
                    esc = commands[esc]
                    continue
                elif esc == "done":
                    return 0
                elif esc == "quit":
                    return -1
                elif esc == "env":
                    show_env(env)
                    continue
                elif esc == "compare":
                    lcomp = True
                    continue
                elif esc == "search":
                    lcomp = False
                    continue
                else:
                    print("["+modstr+"] no such escape command %s" % query)
            elif query in env['registers']:
                target = env['registers'][query]
                if lcomp:
                    get_vas(target)
                    continue
                else:
                    anime = memo.query_anime(target)
                    pretty_print(anime, caller="["+modstr+"]: ")
                    continue
            else:
                try:
                    malid = int(query)
                except ValueError:
                    ids = list(memo.search_anime(query, cli_mode=True))
                    write_registers(ids, env)
                    continue
                else:
                    target = malid
                    if lcomp:
                        get_vas(target)
                        continue
                    else:
                        anime = memo.query_anime(target)
                        pretty_print(anime, caller="["+modstr+"]: ")
                        continue


def main(session, env):
    memo.restore(True)
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
            else:
                trans = cmd
            if trans == "quit":
                v = do_quit(cmd, arg)
                if v == 0:
                    break
                continue
            elif trans == "help":
                do_help(cmd, arg)
                continue
            elif trans == "mode":
                v = do_mode(session, arg, env)
                if v == -1:
                    break
                continue
            elif trans == "search":
                if len(arg) == 0:
                    v = do_query_mode(session, env, compare=False)
                    if v == -1:
                        break
                    continue
            else:
                print("command '%s' not currently supported (perhaps it is mode-specific?)" % cmd)


def cleanup():
    memo.save()

if __name__ == '__main__':
    session = PromptSession()
    env = defaultdict(dict)
    try: 
        main(session, env)
    finally:
        cleanup()
