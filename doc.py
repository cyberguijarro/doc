import anydbm
import sys
import pickle
import difflib

# Configuration

CONTEXT_LINES = 2
SIMILARITY_THRESHOLD = 0.75
DATABASE_NAME = 'doc.db'

# Constants

STATUS_ERROR = 1
STATUS_SUCCESS = 0

# Data types

class Entry:
    def __init__(self, context, text):
        self.before = context[0]
        self.line = context[1]
        self.after = context[2]
        self.text = text

    def get_context(self):
        return (self.before, self.line, self.after)
    
    def set_context(self, context):
        self.before = context[0]
        self.line = context[1]
        self.after = context[2]

# Utility functions and generators

def similarity(a, b):
    return difflib.SequenceMatcher(a=a, b=b).ratio()

def similarity_sequences(a, b):
    return sum([similarity(x,y) for x, y in zip(a, b)]) / max(1, len(a), len(b))

def explore(begin, end, start):
    forward = True
    forward_position = start + 1
    backward_position = start - 1

    yield start
    
    while (backward_position >= begin) or (forward_position < end) :
        if forward and (forward_position < end):
            yield forward_position
            forward_position = forward_position + 1
        elif not forward and (backward_position >= begin):
            yield backward_position
            backward_position = backward_position - 1

        forward = not forward

def find(context, lines, start):
    scores = []

    for line in explore(0, len(lines), start):
        current_context = extract_context(lines, line)
        before_similarities = similarity_sequences(current_context[0], context[0])
        line_similarities = similarity(current_context[1], context[1])
        after_similarities = similarity_sequences(current_context[2], context[2])
        score = (before_similarities * 0.25) + (line_similarities * 0.5) + (after_similarities * 0.25)

        if score == 1.0:
            return line
        elif score >= SIMILARITY_THRESHOLD:
            scores.append((line, score))

    if scores:
        return max(scores, key=lambda s: s[1])[0]

    return None

def load_file(path):
    file = open(path, 'r')
    lines = file.readlines()
    file.close()
    
    return lines

def extract_context(lines, line):
    start = max(0, line - CONTEXT_LINES)
    end = min(line + CONTEXT_LINES + 1, len(lines))

    return (lines[start:line], lines[line], lines[line + 1:end])

# Commands

def put(database, path, line):
    line = int(line) - 1
    lines = load_file(path)
    key = '%s:%s' % (path, line)
    text = ""

    for temp in sys.stdin:
        text += temp

    database[key] = pickle.dumps(Entry(extract_context(lines, line), text))

    return (STATUS_SUCCESS, 'Update successful.')

def get(database, path, line):
    line = int(line) - 1
    key = '%s:%s' % (path, line)

    if key in database.keys():
        entry = pickle.loads(database[key])
        return (STATUS_SUCCESS, entry.text)
    else:
        return (STATUS_ERROR, 'Entry for %s:%s not found.' % (path, line + 1))

def update(database, path):
    lines = load_file(path)
    processed = 0
    updated = 0
    orphaned = 0

    for key in database.keys():
        if key.split(':')[0] == path:
            line = int(key.split(':')[1])
            entry = pickle.loads(database[key])
            print 'processing', line + 1
            processed = processed + 1
            
            if entry.get_context() != extract_context(lines, line):
                previous_line = line
                line = find(entry.get_context(), lines, previous_line)
                
                print previous_line + 1, 'has moved to', line + 1
                
                if line != None:
                    del database[key]
                    key = '%s:%s' % (path, line)
                    entry.set_context(extract_context(lines, line))
                    database[key] = pickle.dumps(entry)
                    updated = updated + 1
                else:
                    orphaned = orphaned + 1
            else:
                print line + 1, 'matched.'

    return (STATUS_SUCCESS, 'Done (%d processed, %d updated, %d orphaned).' % (processed, updated, orphaned))

def remove(database, path, line):
    line = int(line) - 1
    key = '%s:%d' % (path, line)
    
    if key in database.keys():
        del database[key]
        return (STATUS_SUCCESS, '%s:%d removed.' % (path, line + 1))
    else:
        return (STATUS_ERROR, 'No entry found: %s:%d.' % (path, line + 1))

def clean(database, path):
    entries = []
    
    for key in database.keys():
        if key.split(':')[0] == path:
            entries.append(key)

    for entry in entries:
        del database[entry]

    if entries:
        return (STATUS_SUCCESS, '%d entries removed.' % len(entries))
    else:
        return (STATUS_ERROR, 'No entries for %s.' % path)

def _list(database, *args):
    entries = 0

    for key in database.keys():
        path = key.split(':')[0]

        if (len(args) == 0) or (path == args[0]):
            print int(key.split(':')[1]) + 1
            entries = entries + 1

    return (STATUS_SUCCESS, '%d entries listed.' % entries)

def default(database, *args):
    return (STATUS_ERROR, 'Unknown command.')

database = anydbm.open('doc', 'c')
commands = {
    'put': (put, 2),
    'get': (get, 2),
    'update': (update, 1),
    'remove': (remove, 2),
    'clean': (clean, 1),
    'list': (_list, 0)
} 

(status, message) = (STATUS_ERROR, 'No command supplied.')

if len(sys.argv) > 1:
    (method, parameters) = commands.get(sys.argv[1], (default, 0))
    if len(sys.argv) - 2 >= parameters:
        (status, message) = method(database, *sys.argv[2:])
    else:
        (status, message) = (STATUS_ERROR, 'Insufficient parameters.')

print message
database.close()
sys.exit(status)
