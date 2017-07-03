import play
import behavior
import robocup
import constants
import enum
import time
import skills


## Robots repeatedly line up on opposite sides of the field
class Square(play.Play):

    Pause = .1

    min_x = 1 * -constants.Field.Width / 6
    max_x = 1 * constants.Field.Width / 6

    min_y = 2 * constants.Field.Length / 12
    max_y = 4 * constants.Field.Length / 12

    class State(enum.Enum):
        up_right = 0
        up_left = 1
        bottom_left = 2
        bottom_right = 3
        pause = 4

    def __init__(self):
        super().__init__(continuous=True)

        self.side_start = time.time()

        for state in Square.State:
            self.add_state(state, behavior.Behavior.State.running)

        self.add_transition(behavior.Behavior.State.start,
                            Square.State.up_right, lambda: True,
                            'immediately')

        self.add_transition(
            Square.State.up_left,
            Square.State.pause,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'made it to up')

        self.add_transition(
            Square.State.up_right,
            Square.State.pause,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'made it to left')

        self.add_transition(
            Square.State.bottom_left,
            Square.State.pause,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'made it to down')

        self.add_transition(
            Square.State.bottom_right,
            Square.State.pause,
            lambda: self.all_subbehaviors_completed() and time.time() - self.side_start > 1,
            'made it to right')

        self.add_transition(
            Square.State.pause,
            Square.State.up_left,
            lambda: (time.time() - self.pause_start_time) > Square.Pause and self.prev_side == Square.State.bottom_left,
            'pause over')
        self.add_transition(
            Square.State.pause,
            Square.State.up_right,
            lambda: (time.time() - self.pause_start_time) > Square.Pause and self.prev_side == Square.State.up_left,
            'pause over')
        self.add_transition(
            Square.State.pause,
            Square.State.bottom_right,
            lambda: (time.time() - self.pause_start_time) > Square.Pause and self.prev_side == Square.State.up_right,
            'pause over')
        self.add_transition(
            Square.State.pause,
            Square.State.bottom_left,
            lambda: (time.time() - self.pause_start_time) > Square.Pause and self.prev_side == Square.State.bottom_right,
            'pause over')

    def on_enter_up_left(self):
        self.side_start = time.time()
        self.add_subbehavior(skills.move.Move(robocup.Point(self.min_x, self.max_y)), "Robot")

    def on_exit_up_left(self):
        self.remove_all_subbehaviors()
        self.prev_side = Square.State.up_left

    def on_enter_up_right(self):
        self.side_start = time.time()
        self.add_subbehavior(skills.move.Move(robocup.Point(self.max_x, self.max_y)), "Robot")

    def on_exit_up_right(self):
        self.remove_all_subbehaviors()
        self.prev_side = Square.State.up_right

    def on_enter_bottom_left(self):
        self.side_start = time.time()
        self.add_subbehavior(skills.move.Move(robocup.Point(self.min_x, self.min_y)), "Robot")

    def on_exit_bottom_left(self):
        self.remove_all_subbehaviors()
        self.prev_side = Square.State.bottom_left

    def on_enter_bottom_right(self):
        self.side_start = time.time()
        self.add_subbehavior(skills.move.Move(robocup.Point(self.max_x, self.min_y)), "Robot")

    def on_exit_bottom_right(self):
        self.remove_all_subbehaviors()
        self.prev_side = Square.State.bottom_right

    def on_enter_pause(self):
        self.pause_start_time = time.time()

    def execute_running(self):
        for bhvr in self.all_subbehaviors():
            if (bhvr.robot != None):
                pt = bhvr.robot.pos
                pt.y += 1
                bhvr.robot.face(pt)
                #bhvr.robot.angle = 0

