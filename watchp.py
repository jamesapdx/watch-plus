#!/usr/bin/python

import curses, sys, os, time, subprocess

def run_linux(cmd):
    result, err = subprocess.Popen(
                                cmd.split(" "),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                                ).communicate()
    return result.decode("utf-8"), err

class Windows():
    master_windows = []

    def __init__(self, window, cmd, current_time):
        self.window = window
        self.cmd = cmd
        self.creation_time = current_time
        self.window_lines = []
        self.window_columns = []
        self.ticks_per_iter = 1
        self.cooldown_ticks = 4
        self.history_min = 1

        self.frame = [[" "]]
        self.heatmap = [["0"]]

        self.v_position = 0
        self.h_postion = 0

    def frame_generator(self):

        first = True

        while True:
            new_position = len(self.frame)
            self.frame.append([])
            self.heatmap.append([])
            result, error = run_linux("date")
            #result = (result.strip("\n") + ("adf" * 60) + str("\n")) * 60

            # make local variables for the current frame, heatmap, last frame, and last heatmap
            # save them to the actual class arrays (self.frame etc) at the end.  this is much easier to work with
            # frame is a list, each list item is a line of text to be displayed
            # heatmap is a list, each list item is a line of text containing the heatmap values
            frame = result.splitlines()
            frame_length = len(frame)
            last_frame = self.frame[new_position - 1]
            last_frame_length = len(last_frame)
            last_heatmap = self.heatmap[new_position - 1]
            last_heatmap_length = len(last_heatmap)

            # make all lists the same length for ease of processing when comparing current with previous
            # preserve length variables to strip unnecessary lines at the end
            max_lines = max(last_heatmap_length, frame_length)

            frame = frame + ([""] * (max_lines - frame_length))
            last_frame = last_frame + ([""] * (max_lines - last_frame_length))
            last_heatmap = last_heatmap + ([""] * (max_lines - last_heatmap_length))


            for line in range(max_lines):

                # make all variables of the current line the same length for ease of processing
                frame_line_length = len(frame[line])
                last_frame_line_length = len(last_frame[line])
                last_heatmap_line_length = len(last_heatmap[line])

                max_char = max(frame_line_length, last_frame_line_length, last_heatmap_length)

                frame_line = frame[line].rstrip("\n") + (" " * (max_char - frame_line_length + 0))
                x = len(frame_line)
                last_frame_line = last_frame[line] + (" " * (max_char - last_frame_line_length + 0))
                y = len(last_frame_line)
                last_heatmap_line = last_heatmap[line] + ("0" * (max_char - last_heatmap_line_length + 0))
                z = len(last_heatmap_line)


                # if there is no change from the last iteration, just point to the last iteration
                if frame_line == last_frame_line:
                    # set the new frame equal to the last frame
                    self.frame[new_position].append(self.frame[new_position - 1][line])
                    # set heatmap to the last heatmap
                    self.heatmap[new_position].append(self.heatmap[new_position - 1][line])
                    if int(max(last_heatmap_line)) > 1:
                        # cooldown calculation needed, loop through levels and reduce by one
                        for cooldown in range(self.cooldown_ticks + 1, 2, -1):
                            self.heatmap[new_position][line] = last_heatmap_line.replace(str(cooldown),str(cooldown - 1))
                else:
                    # something is different on this line, so go through char by char
                    heatmap_line = ""
                    for char in range(max_char):
                        if frame_line[char] != last_frame_line[char]:
                            # this char is different than last time, set heatmap char to max cooldown
                            heatmap_line = heatmap_line + str(self.cooldown_ticks + 1)
                        else:
                            if int(last_heatmap_line[char]) == 0 or int(last_heatmap_line[char]) == 1 :
                                # if heatmap char is 0 or 1 no change needed, just add
                                heatmap_line = heatmap_line + last_heatmap_line[char]
                            else:
                                # heatmap char must be in cooldown, so subtract 1
                                heatmap_line = heatmap_line + str(int(last_heatmap_line[char]) - 1)
                    self.frame[new_position].append(frame_line)
                    self.heatmap[new_position].append(heatmap_line)


def terminate_curses():
    curses.echo()
    curses.nocbreak()
    curses.curs_set(1)
    curses.endwin()

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
curses.start_color()
stdscr.keypad(True)

try:
    x = Windows(stdscr, "date", 0)
    x.frame_generator()
    #x.display_frame()
except:
    terminate_curses()
    raise

if curses.isendwin() is not True:
    terminate_curses()
