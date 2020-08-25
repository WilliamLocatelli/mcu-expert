''' Creates a GUI which allows user to specify which films they have seen and which films they
would like to see, and gives them recommendations as to which movies they should watch in between.

This python GUI is currently broken. However, it is entirely unnecessary, because the program can easily
be run locally using the node.js app.
'''
from LegacyFiles.MarvelTracker import Movie
import Recommender as Rec
from LegacyFiles.graphics import *

WIDTH = 1200
HEIGHT = 600
NUM_CHOSEN = 0
HOVER_COLOR = color_rgb(76, 237, 78)
SELECTED_COLOR = color_rgb(31, 222, 34)
CHOSEN_COLOR = color_rgb(18, 173, 206)
WATCHED_COLOR = color_rgb(83, 116, 81)
CHILDREN_COLOR = color_rgb(206, 191, 18)
BUTTON_COLOR = color_rgb(210, 222, 31)
INSTRUCTION_TEXT = None
CHILDREN = []
WATCHED = []
CHANGED = False
NEXT_TEXT = None
REC_TEXT = None
BUTTONS = {}

# draws the window
def draw_window():
    # sort each movie by series
    series = {}
    for movie in Rec.MOVIES.values():
        if movie.series not in series:
            series[movie.series] = [movie]
        else:
            series[movie.series].append(movie)

    x_pos = 3
    # set position of each movie
    for movie_series in series:
        y_pos = 5
        for movie in series[movie_series]:
            point = Point(x_pos, y_pos)
            movie.set_point(point, height=8, width=14.5)
            y_pos = y_pos + 8*1.5
        x_pos = x_pos + 14.5*1.1
    '''x_pos = 5
    y_pos = 5
    # set position of each movie
    for movie in MOVIES.values():
        point = Point(x_pos, y_pos)
        movie.set_point(point, height=8, width=14)
        x_pos = x_pos + 10 * 1.5
        if x_pos > 160:
            y_pos = y_pos + 8 * 1.5
            x_pos = 5'''

    # draw window
    win = GraphWin(title="MCU Watchlist Generator", width=WIDTH, height=HEIGHT, autoflush=False)
    win.setCoords(0, 180*HEIGHT/WIDTH, 180, 0)
    win.bind('<Motion>', motion)
    for movie in Rec.MOVIES.values():
        movie.draw(win)

    next_button = Rectangle(Point(80, 60), Point(90, 65))
    next_button.setFill(BUTTON_COLOR)
    next_text = Text(next_button.getCenter(), text="Next")
    next_button.draw(win)

    BUTTONS["Next"] = {"Button": next_button, "Text": next_text}
    next_text.draw(win)

    prev_button = Rectangle(Point(60, 60), Point(70, 65))
    prev_button.setFill(BUTTON_COLOR)
    prev_text = Text(prev_button.getCenter(), text="Back")
    BUTTONS["Previous"] = {"Button": prev_button, "Text": prev_text}

    global INSTRUCTION_TEXT
    INSTRUCTION_TEXT = Text(Point(50, 70), text="Select the movies you have already seen.")
    INSTRUCTION_TEXT.setSize(20)
    INSTRUCTION_TEXT.draw(win)
    global REC_TEXT
    REC_TEXT = Text(Point(160, 50), text="")
    update()
    return win


# runs the main program
def run_program(win):
    global NUM_TIES
    global REC_TEXT
    global CHANGED
    global CHILDREN
    level = 1
    watched = []
    selected = watched
    #children = []
    subgraph = []
    input_box = Entry(Point(INSTRUCTION_TEXT.getAnchor().getX() + 50, INSTRUCTION_TEXT.getAnchor().getY()), 10)
    input_box.setFill("white")
    input_box.setText("1")
    while (win.isOpen()):
        try:
            p = win.getMouse()
        except:
            break
        # Next Button
        if 80 < p.getX() < 90 and 60 < p.getY() < 65:
            # stage 1-> stage 2
            if level == 1:
                level = 2
                selected = CHILDREN
                for movie in watched:
                    Movie.open.remove(movie)
                    movie.my_square.setFill("gray")
                for movie in CHILDREN:
                    movie.my_square.setFill(SELECTED_COLOR)
                    movie.selected = True
                INSTRUCTION_TEXT.setText("Select the movies you would like to see.")
                if BUTTONS["Previous"]["Text"].getText() == "Reset":
                    BUTTONS["Previous"]["Text"].setText("Back")
                else:
                    BUTTONS["Previous"]["Button"].draw(win) #draw the back button
                    BUTTONS["Previous"]["Text"].draw(win)
            # stage 2-> stage 3
            elif level == 2:
                if len(CHILDREN) == 0:
                    INSTRUCTION_TEXT.setText("You must select at least 1 movie you would like to see.")
                else:
                    level = 3
                    Movie.open.clear()
                    for movie in CHILDREN:
                        movie.my_square.setFill(CHILDREN_COLOR)
                    INSTRUCTION_TEXT.setText("How many additional movies are you willing to watch?")
                    input_box.draw(win)
            #stage 3->stage 4
            elif level == 3:
                global NUM_CHOSEN
                if not str.isdigit(input_box.getText()):
                    input_box.setText("")
                    INSTRUCTION_TEXT.setText("How many additional movies are you willing to watch?\nOnly numbers are allowed.")
                else:
                    level = 4
                    if CHANGED or not NUM_CHOSEN == int(input_box.getText()):
                        CHANGED = False
                        NUM_CHOSEN = int(input_box.getText())
                        subgraph = Rec.find_best_subgraph(watched, CHILDREN, NUM_CHOSEN, "Recent")
                        order = Rec.watch_order(watched, subgraph)
                        #watched_string = "Already Watched:\n" + "\n".join(t.name for t in watched)
                        rec_string = "\nRecommended Watchlist:\n" + "\n\n".join(order)
                        REC_TEXT.setText(rec_string)
                        REC_TEXT.undraw()
                        REC_TEXT.draw(win)
                    for movie in Rec.MOVIES.values():
                        if movie not in watched and movie not in CHILDREN:
                            if movie in subgraph:
                                movie.my_square.setFill(CHOSEN_COLOR)
                            else:
                                movie.my_square.setFill("white")
                    input_box.undraw()
                    INSTRUCTION_TEXT.setText("Here are your recommendations!")

                    BUTTONS["Next"]["Button"].undraw()
                    BUTTONS["Next"]["Text"].undraw()
                    #NEXT_TEXT.setText("Reset")
        #back button
        if 60 < p.getX() < 70 and 60 < p.getY() < 65:
            # stage 4-->stage 3
            if level == 4:
                level = 3
                Rec.GRAPHS_CHECKED = 0
                Rec.CURRENT_ANCESTOR_TIER = 0
                INSTRUCTION_TEXT.setText("How many additional movies are you willing to watch?")
                BUTTONS["Next"]["Button"].draw(win)
                BUTTONS["Next"]["Text"].draw(win)
                input_box.draw(win)
            # stage 3--> stage 2
            elif level == 3:
                level = 2
                INSTRUCTION_TEXT.setText("Select the movies you would like to see.")
                input_box.undraw()
                selected = CHILDREN
                for movie in Rec.MOVIES.values():
                    if movie not in watched:
                        Movie.open.append(movie)
                        if movie not in CHILDREN:
                            movie.my_square.setFill("white")
                        else:
                            movie.my_square.setFill(SELECTED_COLOR)
            # stage 2--> stage 1 (disallowing repetition)
            elif level == 2:
                level = 1
                INSTRUCTION_TEXT.setText("Select the movies you have already seen.")
                selected = watched
                for movie in Rec.MOVIES.values():
                    if movie not in Movie.open:
                        Movie.open.append(movie)
                    if movie in watched:
                        movie.selected = True
                        movie.my_square.setFill(SELECTED_COLOR)
                    else:
                        movie.selected = False
                        if movie in CHILDREN:
                            movie.my_square.setFill(CHILDREN_COLOR)
                if len(CHILDREN) > 0 or len(watched) > 0:
                    BUTTONS["Previous"]["Text"].setText("Reset")
                else:
                    BUTTONS["Previous"]["Button"].undraw() #undraw the back button
                    BUTTONS["Previous"]["Text"].undraw()
            # reset button
            elif level == 1:
                watched.clear()
                CHILDREN.clear()
                for movie in Rec.MOVIES.values():
                    movie.selected = False
                    movie.my_square.setFill("white")
                REC_TEXT.undraw()
                BUTTONS["Previous"]["Button"].undraw()  # undraw the back button
                BUTTONS["Previous"]["Text"].undraw()
                BUTTONS["Previous"]["Text"].setText("Back")
        for movie in Movie.open:
            if movie.p1.getX() < p.getX() < movie.p2.getX() and movie.p1.getY() < p.getY() < movie.p2.getY():
                CHANGED = True
                if not movie.selected:
                    if movie in CHILDREN:
                        CHILDREN.remove(movie)
                    selected.append(movie)
                    movie.selected = True
                    movie.my_square.setFill(SELECTED_COLOR)
                else:
                    movie.my_square.setFill(HOVER_COLOR)
                    selected.remove(movie)
                    movie.selected = False


# tracks motion
def motion(event):
    global CHILDREN
    x = 180*event.x/WIDTH
    y = 180*event.y/WIDTH
    # if we hover over an open movie, show which movies will be unlocked if we watch this movie.
    for movie in Movie.open:
        if movie.p1.getX() < x < movie.p2.getX() and movie.p1.getY() < y < movie.p2.getY():
            movie.my_square.setFill(HOVER_COLOR)
        # if we are not hovering over this movie, reset the colors back to normal
        else:
            if movie.selected:
                movie.my_square.setFill(SELECTED_COLOR)
            elif movie in CHILDREN:
                movie.my_square.setFill(CHILDREN_COLOR)
            else:
                movie.my_square.setFill("white")
    for button in BUTTONS.values():
        button = button["Button"]
        if button.p1.getX() < x < button.p2.getX() and button.p1.getY() < y < button.p2.getY():
            button.setFill(HOVER_COLOR)
        # if we are not hovering over this movie, reset the colors back to normal
        else:
            button.setFill(BUTTON_COLOR)


if __name__ == '__main__':
    Rec.import_weighted_from_csv()
    Rec.import_data_from_csv()
    win = draw_window()
    run_program(win)
