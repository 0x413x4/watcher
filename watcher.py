#!/usr/bin/env python3
# @alexa - 2019
""" watcher.py
Small program to monitor linux filesystem events. It is based on the inotify
linux kernel API, and can be used to for various purposes such as reverse
engineering and penetration testing.

Usage:
watcher.py [options] <directory>
"""
__author__ = "alexa"
__version__ = "1.0"
__status__ = "dev"
__licence__ = "MIT"

import argparse
import colorama
import inotify.adapters
import os

# Define colours for events
colorama.init(autoreset=True)
_EVENTS = {
    'IN_ACCESS': colorama.Fore.WHITE + '[!] {} accessed: {}',
    'IN_ATTRIB': colorama.Fore.CYAN + '[!] {} metadata has changed: {}',
    'IN_CLOSE_NOWRITE': colorama.Fore.WHITE + '[!] {} closed {}',
    'IN_CLOSE_WRITE': colorama.Fore.WHITE + '[!] {} closed {}',
    'IN_CREATE': colorama.Fore.GREEN + '[+] {} created: {}',
    'IN_DELETE': colorama.Fore.RED + '[-] {} deleted: {}',
    'IN_DELETE_SELF': colorama.Fore.RED + '[-] File monitored deleted',
    'IN_MODIFY': colorama.Fore.YELLOW + '[!] {} modified: {}',
    'IN_MOVED_FROM': colorama.Fore.YELLOW + '[+] {} moved from: {}',
    'IN_MOVED_TO': colorama.Fore.YELLOW + '[+] {} moved to: {}',
    'IN_MOVE_SELF': colorama.Fore.YELLOW + '[+] {} monitored moved: {}',
    'IN_OPEN': colorama.Fore.WHITE + '[!] {} opened: {}'
}


_DEFAULT_EVENTS = [
    'IN_CREATE',
    'IN_DELETE',
    'IN_DELETE_SELF',
    'IN_MOVED_FROM',
    'IN_MOVED_TO',
    'IN_MOVE_SELF'
]


_VERBOSE_EVENTS = [
    'IN_CREATE',
    'IN_DELETE',
    'IN_DELETE_SELF',
    'IN_MOVED_FROM',
    'IN_MOVED_TO',
    'IN_MOVE_SELF',
    'IN_MODIFY',
    'IN_ATTRIB'
]


_ALL_EVENTS = [
    'IN_ACCESS',
    'IN_ATTRIB',
    'IN_CLOSE_NOWRITE',
    'IN_CLOSE_WRITE',
    'IN_CREATE',
    'IN_DELETE',
    'IN_DELETE_SELF',
    'IN_MODIFY',
    'IN_MOVED_FROM',
    'IN_MOVED_TO',
    'IN_MOVE_SELF',
    'IN_OPEN'
]


def monitor(directory, recursive=False, events=_DEFAULT_EVENTS):
    # Check directory exist and is readable
    if not os.path.exists(directory):
        print('[!] ERROR: {} does not exist'.format(directory))
        exit(1)

    # Event subscription
    if recursive:
        watcher = inotify.adapters.InotifyTree(directory)
    else:
        watcher = inotify.adapters.Inotify()
        watcher.add_watch(directory)

    # Print events as they come
    for e in watcher.event_gen(yield_nones=False):
        (_, tn, path, filename) = e
        if tn[0] in events and 'IN_EXCL_UNLINK' not in tn:
            f = os.path.join(path, filename)
            if 'IN_ISDIR' in tn:
                print(_EVENTS[tn[0]].format('directory', f))
            else:
                print(_EVENTS[tn[0]].format('file', f))


if __name__ == '__main__':
    _description = 'Monitor filesystem changes on Linux'
    parser = argparse.ArgumentParser(description=_description)

    # Directory
    parser.add_argument('directory',
                        action='store',
                        help='directory to monitor')

    # Recursive watching
    parser.add_argument('-r', '--recursive',
                        action='store_true',
                        help='enable recursive watching')

    # Events
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true')
    group.add_argument('-a', '--all', action='store_true')
    group.add_argument('--events', nargs='*',
                       action='store', choices=_ALL_EVENTS,
                       help='individual events to monitor')

    # Prepare options
    args = parser.parse_args()

    if args.events is not None:
        events = args.events
    elif args.verbose:
        events = _VERBOSE_EVENTS
    elif args.all:
        events = _ALL_EVENTS
    else:
        events = _DEFAULT_EVENTS

    cm = colorama.Fore.MAGENTA
    ct = colorama.Fore.RED

    print(ct + '=============================================================')
    print(ct + '                        WATCHER.PY')
    print(ct + '                        @413x4sec - 2019')
    print(ct + '=============================================================')
    print

    print(cm + '\nConfiguration:')
    print(cm + "|--> Directory watched : {}".format(args.directory))
    print(cm + "|--> Recursive watching: {}".format(args.recursive))
    print(cm + "|--> Events monitored: ")
    for e in events:
        print(cm + "    * {}".format(e))
    print('')

    try:
        monitor(args.directory, args.recursive, events)
    except KeyboardInterrupt:
        print('Stopped monitoring')
