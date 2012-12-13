# doc: a source code annotation tool

The idea behind this simple tool is to provide an automated mechanism to store source code comments in a separate database file.

Keeping source code and human-targeted documentation has various advantages:

* Documentation can be loaded and displayed on demand.
* Cleaner code, even against "folding" text editors.
* Source code and documentation can be distributed separatedly.
* Various documentation flavours can be used (development, API, commentary, etc.) and distributed independently.

## Command line foo

You may want to skip all the rough CLI stuff and move directly to the text editor integration (see next sections).

### Adding comments to your source file

Starting documentation for your project has no overhead whatsoever, simply use the put command:

<pre>
$ doc put source.py 10
This function does cool stuff.[CTRL-D]
$
</pre>

The put command takes any number of text lines from the standard input and associates it to the source file and line specified in the command line.

### Retrieving comments

Retrieving comments is just as simple as creating them:

<pre>
$ doc get source.py 10
This function does cool stuff.
$
</pre>

### What if my source code changes?

Don't sweat it. doc has a powerful algorithm to detect and fix source code line changes and movements within your source files. Just make sure you run the "update" command every now and then (every time you save is even better):

<pre>
$ doc update source.py
</pre>

### Removing comments

Source code annotations can be removed just as simply as they are added.

<pre>
$ doc remove source.py 10
</pre>

### Clearing all comments for a source file

<pre>
$ doc clean source.py
</pre>

### Listing lines with comments

<pre>
$ doc list source.py
21
32
58
</pre>

Omitting the first parameter reveals all entries within the database:

<pre>
$ doc list
source.py 21
source.py 32
source.py 58
</pre>

## Am I supossed to do this by hand?

No. doc is intendend to be used through text editor or IDE plugins.

### vim

The VIM plugin automates a lot of the previously seen command line work. Just install the plugin (copy doc.vim to ~/.vim/plugins) and enjoy all the good stuff:

#### Load and display comment marks

All comments are loaded automatically upon file load, and all affected lines are marked using vim's "signs" feature. You can also reload all tags for the current buffer using:

<pre>
:DocLd
</pre>

#### Add a comment

Just move to the source line of you desire and type:

<pre>
:Doc
</pre>

and use the pop-up buffer to write your document your masterpiece. Once finished, use:

<pre>
:w
</pre>

to save it, or alternatively:

<pre>
:wq
</pre>

to save and close the buffer (yes, you can do anything else supported by regular vim buffers).

#### Remove a comment

Just move to the offending source line and use:

<pre>
:DocDel
</pre>

#### Update comment database

Every time you save a buffer, the database portion of the file is automatically updated. Also, you can update it manually for the current active buffer:

<pre>
:DocUpd
</pre>

### Other text editors

I'm not going to learn how to write plugins for all of the exising IDEs and text editors out there. Soooooo, contributions are much welcome.

## The database format

All comments and necessary metadata is stored in a sorted, plain-text, JSON file with human-friendly line breaks and identation. I know there are much more efficient solutions out there (k/v dbm's, sqlite), but those would just kill any kind of team (VCS) interoperability.

Current format should keep rebasing and merging operations as manageable as it can be, just make sure to always commit your updated documentation database together with the affected source files.
