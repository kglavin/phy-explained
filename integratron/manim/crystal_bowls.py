"""Manim scenes of a crystal bowl vibrating and of two bowls beating.

Render from the integratron/manim directory (720p, about a minute each):
    ../.venv/bin/manim -qm crystal_bowls.py VibratingBowl TwoBowlsBeating
    cp media/videos/crystal_bowls/720p30/VibratingBowl.mp4 videos/vibrating_bowl.mp4
    cp media/videos/crystal_bowls/720p30/TwoBowlsBeating.mp4 videos/two_bowls_beating.mp4

Manim needs the packages in ../requirements-manim.txt.

The motion and the pitch gap are exaggerated so they can be seen, as in
notebook 07.
"""
import numpy as np
from manim import (
    BLUE, BLUE_E, DEGREES, DOWN, GREY_B, LEFT, ORANGE, RED, RIGHT, TEAL, UP, WHITE,
    YELLOW, Axes, Circle, DashedVMobject, Dot, Dot3D, Line, ParametricFunction, Scene,
    Surface, Text, ThreeDScene, ValueTracker, VGroup, always_redraw, interpolate_color,
    linear,
)

PATTERN = 2          # the 4-lobed pattern, n = 2
ENLARGE = 0.15       # rim displacement at the peak of a cycle, as a fraction of the radius
RADIUS = 2.0         # bowl radius in scene units
NODE_ANGLES = (np.arange(2 * PATTERN) + 0.5) * np.pi / PATTERN


def bowl_point(psi, phi, bend):
    # Hemispherical shell open at the top: psi = 0 at the base, pi/2 at the rim.
    # The wall bends in and out, growing toward the rim.
    radius = RADIUS * np.sin(psi) * (1 + bend * np.sin(psi) ** 2 * np.cos(PATTERN * phi))
    return np.array([radius * np.cos(phi), radius * np.sin(phi), -RADIUS * np.cos(psi)])


class VibratingBowl(ThreeDScene):
    def construct(self):
        cycles = ValueTracker(0.0)

        def bend():
            return ENLARGE * np.cos(2 * np.pi * cycles.get_value())

        def make_bowl():
            b = bend()
            bowl = Surface(lambda u, v: bowl_point(u, v, b), u_range=[0.02, np.pi / 2],
                           v_range=[0, 2 * np.pi], resolution=(12, 48),
                           fill_opacity=0.95, stroke_width=0.3, stroke_color=BLUE_E)
            # Colour each face by how far the wall is pushed out (red) or in (blue)
            for face in bowl:
                u = (face.u1 + face.u2) / 2 if hasattr(face, "u1") else np.pi / 2
                v = (face.v1 + face.v2) / 2 if hasattr(face, "v1") else 0.0
                w = b / ENLARGE * np.sin(u) ** 2 * np.cos(PATTERN * v)
                face.set_fill(interpolate_color(BLUE, RED, (w + 1) / 2), opacity=0.95)
            return bowl

        def make_rim():
            b = bend()
            return ParametricFunction(lambda v: bowl_point(np.pi / 2, v, b),
                                      t_range=[0, 2 * np.pi], color=YELLOW, stroke_width=4)

        nodes = VGroup(*[Dot3D(bowl_point(np.pi / 2, a, 0.0), radius=0.07, color=WHITE)
                         for a in NODE_ANGLES])
        title = Text("A crystal bowl's 4-lobed vibration", font_size=34).to_corner(UP + LEFT)
        note = Text("motion enlarged many thousand times, slowed about 260 times",
                    font_size=20, color=GREY_B).to_corner(DOWN + LEFT)
        key = Text("red: wall out   blue: wall in   white: nodes, never move",
                   font_size=20, color=GREY_B).next_to(note, UP, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(title, note, key)

        self.set_camera_orientation(phi=62 * DEGREES, theta=-60 * DEGREES, zoom=1.1)
        self.add(always_redraw(make_bowl), always_redraw(make_rim), nodes)
        self.begin_ambient_camera_rotation(rate=0.25)
        self.play(cycles.animate.set_value(10), run_time=14, rate_func=linear)
        self.stop_ambient_camera_rotation()


class TwoBowlsBeating(Scene):
    def construct(self):
        cycles_per_beat = 8                      # bowl 2 makes 9 cycles while bowl 1 makes 8
        ratio = (cycles_per_beat + 1) / cycles_per_beat
        t = ValueTracker(0.0)                    # time in cycles of bowl 1

        def rim(centre, phase, colour):
            def point(v):
                r = 1.1 * (1 + ENLARGE * np.cos(phase) * np.cos(PATTERN * v))
                return centre + np.array([r * np.cos(v), r * np.sin(v), 0])
            return ParametricFunction(point, t_range=[0, 2 * np.pi], color=colour,
                                      stroke_width=5)

        left, right = np.array([-3.2, 1.7, 0]), np.array([3.2, 1.7, 0])
        guides = VGroup(*[DashedVMobject(Circle(radius=1.1, color=GREY_B, stroke_width=1.5)
                                         .move_to(c), num_dashes=40) for c in (left, right)])
        rim_1 = always_redraw(lambda: rim(left, 2 * np.pi * t.get_value(), WHITE))
        rim_2 = always_redraw(lambda: rim(right, 2 * np.pi * t.get_value() * ratio, TEAL))
        labels = VGroup(Text("bowl 1", font_size=24).next_to(guides[0], UP, buff=0.15),
                        Text("bowl 2, 9/8 the pitch", font_size=24, color=TEAL)
                        .next_to(guides[1], UP, buff=0.15))

        axes = Axes(x_range=[0, cycles_per_beat, 1], y_range=[-2.2, 2.2, 1],
                    x_length=12, y_length=2.6, tips=False,
                    axis_config={"color": GREY_B, "stroke_width": 1.5}).to_edge(DOWN, buff=0.6)
        bowl_1 = axes.plot(lambda x: np.cos(2 * np.pi * x), color=GREY_B, stroke_width=1.5)
        bowl_2 = axes.plot(lambda x: np.cos(2 * np.pi * x * ratio), color=TEAL, stroke_width=1.5)
        both = axes.plot(lambda x: np.cos(2 * np.pi * x) + np.cos(2 * np.pi * x * ratio),
                         color=BLUE, stroke_width=3)
        envelope = DashedVMobject(axes.plot(
            lambda x: abs(2 * np.cos(np.pi * x / cycles_per_beat)), color=ORANGE,
            stroke_width=2), num_dashes=60)
        cursor = always_redraw(lambda: Line(axes.c2p(t.get_value(), -2.2),
                                            axes.c2p(t.get_value(), 2.2), color=YELLOW))
        marker = always_redraw(lambda: Dot(axes.c2p(
            t.get_value(),
            np.cos(2 * np.pi * t.get_value()) + np.cos(2 * np.pi * t.get_value() * ratio)),
            color=YELLOW))
        key = Text("blue: the sound of both   orange: loudness", font_size=20,
                   color=GREY_B).next_to(axes, UP, buff=0.1)
        state = always_redraw(lambda: Text(
            "in step: loud" if abs(np.cos(np.pi * t.get_value() / cycles_per_beat)) > 0.7
            else ("out of step: quiet"
                  if abs(np.cos(np.pi * t.get_value() / cycles_per_beat)) < 0.3
                  else "drifting apart" if t.get_value() < cycles_per_beat / 2
                  else "drifting back"),
            font_size=28, color=YELLOW).move_to(np.array([0, 1.7, 0])))
        note = Text("pitch gap and motion exaggerated", font_size=18,
                    color=GREY_B).to_corner(UP + RIGHT, buff=0.2)

        self.add(guides, labels, axes, bowl_1, bowl_2, both, envelope, key, note)
        self.add(rim_1, rim_2, cursor, marker, state)
        self.play(t.animate.set_value(cycles_per_beat), run_time=16, rate_func=linear)
        self.wait(0.5)
