# tally2obsi-py
A script to make migrating Notally notes to Obsidian possible!

## Usage
Just throw the source file and your 'NotallyDatabase' file into a folder (preferrably a new, temporary one), then run the script with Python. As shrimple as that!

![image](https://github.com/nucspl/tally2obsi-py/assets/80261260/9a546bc1-48ef-4702-9b23-dc54364a6c8d)

## Questions
### Why bother making this?
Because I've long wanted to integrate my Notally notes into my Obsidian vault. What prevented me from doing so was the loss of creation timestamps that are preserved in the database—an issue I've been trying to mitigate with my other notes.

### Mac / Linux?
This script was made with Windows in mind, sorry. POSIX systems seem to be allergic to altering creation timestamps. Though, all you really have to do is modify the `scons` method, the formatted timestamp, and pass your respective system's equivalent commands to it. Here's some notes that I've taken down on the matter:
- On POSIX, `touch` can't manipulate creation timestamps, so there's no unified solution for both MacOS and Linux.
- On MacOS, I've read that [`SetFile`](https://discussions.apple.com/thread/250821280?answerId=251566149022) works, but it would need Xcode installed on the user end.
- On Linux, there's [`debugfs`](https://unix.stackexchange.com/a/36024), but I'm not confident in implementing such a thing.

### Do you have anything against Notally?
No, not at all! In fact, I appreciate the how well it works for me when notetaking on the go. It's a straight-forward, no-nonsense app, and I love it! You can go get it [here.](https://github.com/OmGodse/Notally)
