import behavior
import constants
import enum
import math
import play
import robocup
import role_assignment
import skills
import time


## Robots repeatedly line up on opposite sides of the field
class Square(play.Play):

    Pause = 2.0

    min_x = -constants.Field.Width / 6
    max_x = constants.Field.Width / 6

    min_y = constants.Field.Length / 6
    max_y = 2 * constants.Field.Length / 6

    class State(enum.Enum):
        up_right = 0
        up_left = 1
        bottom_left = 2
        bottom_right = 3
        pause = 4
        orient = 5

    def __init__(self):
        super().__init__(continuous=True)

        self.side_start = time.time()

        for state in Square.State:
            self.add_state(state, behavior.Behavior.State.running)

        self.add_transition(behavior.Behavior.State.start, Square.State.orient,
                            lambda: True, 'immediately')

        self.add_transition(
            Square.State.orient, Square.State.up_right,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'oriented')

        self.add_transition(
            Square.State.up_left, Square.State.pause,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'made it to up')

        self.add_transition(
            Square.State.up_right, Square.State.pause,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'made it to left')

        self.add_transition(
            Square.State.bottom_left, Square.State.pause,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'made it to down')

        self.add_transition(
            Square.State.bottom_right, Square.State.pause,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'made it to right')

        self.add_transition(
            Square.State.pause, Square.State.up_left,
            lambda: (time.time() - self.pause_start_time) > Square.Pause and self.prev_side == Square.State.bottom_left,
            'pause over')
        self.add_transition(
            Square.State.pause, Square.State.up_right,
            lambda: (time.time() - self.pause_start_time) > Square.Pause and self.prev_side == Square.State.up_left,
            'pause over')
        self.add_transition(
            Square.State.pause, Square.State.bottom_right,
            lambda: (time.time() - self.pause_start_time) > Square.Pause and self.prev_side == Square.State.up_right,
            'pause over')
        self.add_transition(
            Square.State.pause, Square.State.bottom_left,
            lambda: (time.time() - self.pause_start_time) > Square.Pause and self.prev_side == Square.State.bottom_right,
            'pause over')

    def role_requirements(self):
        reqs = super().role_requirements()
        for req in role_assignment.iterate_role_requirements_tree_leaves(reqs):
            req.required_shell_id = 1
        return reqs

    def on_enter_orient(self):
        self.side_start = time.time()
        self.add_subbehavior(
            skills.face.Face(
                robocup.Point(self.min_x, self.max_y), math.pi * 1.5), "Robot")

    def on_exit_orient(self):
        self.remove_all_subbehaviors()

    def on_enter_up_left(self):
        self.side_start = time.time()
        self.add_subbehavior(
            skills.move.Move(robocup.Point(self.min_x, self.max_y)), "Robot")

    def on_exit_up_left(self):
        self.remove_all_subbehaviors()
        self.prev_side = Square.State.up_left

    def on_enter_up_right(self):
        self.side_start = time.time()
        self.add_subbehavior(
            skills.move.Move(robocup.Point(self.max_x, self.max_y)), "Robot")

    def on_exit_up_right(self):
        self.remove_all_subbehaviors()
        self.prev_side = Square.State.up_right

    def on_enter_bottom_left(self):
        self.side_start = time.time()
        self.add_subbehavior(
            skills.move.Move(robocup.Point(self.min_x, self.min_y)), "Robot")

    def on_exit_bottom_left(self):
        self.remove_all_subbehaviors()
        self.prev_side = Square.State.bottom_left

    def on_enter_bottom_right(self):
        self.side_start = time.time()
        self.add_subbehavior(
            skills.move.Move(robocup.Point(self.max_x, self.min_y)), "Robot")

    def on_exit_bottom_right(self):
        self.remove_all_subbehaviors()
        self.prev_side = Square.State.bottom_right

    def on_enter_pause(self):
        self.pause_start_time = time.time()
