Wedgedle Features:

Necessary before release
~~1. Help Button~~
~~2. Import all characters~~
~~	2a. images for each character~~
~~3. Character drop down menu~~
5. polish win/loss modal (and maybe help modal)
	5a. add timer until next reset

Post Release improvements (not in order)
1. Game Archive
2. Stat Tracking (win%, avg guesses, etc.)
3. wait until animation finishes before next submission
4. arrow key navigation for dropdown
5. prevent duplicate guesses
6. update autofilling logic (some sort of heirarchy?)
7. continue game on refresh rather than resetting
8. create base_game.html template and extend wedgedle for future games
9. fix midnight refresh causing answer to change when page is not refreshed


v1 Feedback

Logic/Bugs
4. Fix Timer to reset at proper time
	notes: fixed reset timer to sync (need to test). slight clock skew maybe fix in future
~~5. Correct logic to determine answer (compare name values instead of category correctness)~~

QoL
2. Work on faction partial correctness ambiguity
	2a. Faction is yellow even if all elements are correct but missing other factions
~~3. Add give up button~~
~~6. Endless mode~~

UI
1. Adjust colors
	1a. Green and Yellow too close
	1b. Colors too transparent
	1c. Incorrect should be gray or red
~~7. adjust font (capital i written as H)~~

