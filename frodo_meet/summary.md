# Frodo Meet
Author: Sunny Lin\
Last edited: Jul 6, 25

---
### Meeting Entries
Refer to the [sample](meeting_entries_sample.txt) file for an example of what entries would look like.

Data for meeting plans will be stored in a text file ([meeting_entries.txt](host_files/meeting_entries.txt)) as entries.

Entries are separated by empty lines.\
Each entry consists of 5 lines for 5 pieces of info:
1. Title.
2. Time: `YYYY MM DD HH mm`.
3. Details.
    - Can store any single **formatted** Discord message.
4. Participants: list of pings, separated by spaces.
    - For **members**, use their <u>user ID</u>.
    - For **roles**, use `&…`, where … is the <u>role ID</u>.
    - For **everyone**, use `everyone`.
    - **Here** seems reduntant for our purposes, but it works like everyone nonetheless.
5. Labels: list of labels, separated by spaces.

Entries are stored in <mark>chronological order based on date</mark>.
- i.e. The first entry in the file should be the closest upcoming one.
