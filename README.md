# Here are the UofT Visual Arts Club's Discord bots.
Author: Sunny Lin\
Last edited: Jul 6, 25

---
### Important
This Github repository should be kept <mark>private</mark>:
> Certain files contain sensitive data (private bot tokens).\
Unauthorised access to this data could allow someone to take control of the bots, thereby causing damage to them and/or the Discord server(s).

---
### Implementation
Currently, the bots are programmed in **Python** using the Python discord package.

I've also included a a rough [template](bot_template.py) file that I wrote for starting to program new Discord bots in case the club ever wants more.

---
### Organisation

Refer to [Frodo Meet](frodo_meet) as an example bot folder.

All bots should have their own folder under this repo, and all files specific to a bot should be kept in their folder.\
Furthermore, all files required for hosting should be in a **files** subfolder (other than the [common](common_bot_helper.py) bot helper file).
> A bot will likely have these files for hosting:
> - Driver file: Uses Discord API to communicate with Discord. Uses functions from helper files to do computation & get outputs ([e.g.](frodo_meet/host_files/frodo_meet.py)).
> - Helper file(s): Contains helper functions for computing a bot's output. Isolated from Discord functions to allow easy testing ([e.g.](frodo_meet/host_files/frodo_meet_helper.py)).
> - Data file(s): If a bot needs to store data. Likely written to/fetched from by helper files ([e.g.](frodo_meet/host_files/meeting_entries.txt)).

When editing a bot or starting a new one, try to be consistent with its and other bots' organisation, unless the bot's functionality requires otherwise.

---
### Hosting
…

---
### Want to make changes?
#### Minor changes
If you want to make minor changes, feel free to do them on the spot.
- This includes small corrections to code, comments, or documentation.

#### Larger changes
If you want to make larger changes to a bot's **backend implementation**, discuss with fellow webmasters.
- This includes rewriting functions, algorithms, or even entire files.

If you want to add to/alter a bot's **frontend behaviour**, consult with the rest of the exec team as well (or just **administrative roles at least**).

#### Tips
Upon replacing blocks of code, **comment** old code and keep it in the file for future reference.
> If commented code gets too crowded, designate a dedicated section for deprecated code (e.g. at the bottom of the file).\
If a large enough portion of a file's code has been replaced, writing a new file could be more efficient (follow instructions below).

Upon replacing entire files, move old files into the [**archive**](archive) so they can always be referred back to.
> The internal organisation of the archive is up to future webmasters' discretion.\
I suggest at least adding to the deprecated file names the **year they were replaced** (i.e. current year, relatively speaking).
> - E.g. If this year was 2025, then `README.md` would become `README-2025.md` in the archive.

Moreover, always employ good code practices:
- Write readable code (meaningful names, type annotations, organise & distinguish tasks).
- Express your ideas (write code comments, function docstrings & tests, file documentations, meaningful commit messages).
- Communicate with the team (announce when you've made significant changes, meaningful commit messages).
- Write <mark>TODO</mark> comments for any potential development.
    - Small tasks can be written where they should be.
    - Larger tasks can be written below the file description at the top.

This will help not only you but also fellow & future webmasters.

---
###
And last but not least, <mark>communicate with the team, be responsible, and do your best!</mark>\
Oh, and **have fun** as well ; )

### Cheers!
\- SL