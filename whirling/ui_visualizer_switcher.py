from rx.subject.behaviorsubject import BehaviorSubject
from whirling.ui_core import UIElement, UIDock
from whirling import colors
from whirling.primitives import Rect
from whirling.VisualizationManager import visualizers



class UIVisualizerSwitcher(UIDock):
    def __init__(self, current_visualizer: BehaviorSubject, rect: Rect,
            bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

        self.visualizer = None

        current_visualizer.subscribe(self.change_visualizer)

    def get_visualizer_rect(self):
        padding_percent = .05
        padding = self.rect.width * padding_percent
        return Rect(
            self.rect.left + padding,
            self.rect.top - padding,
            self.rect.right - padding,
            self.rect.bottom + padding
        )

    def draw(self):
        super().draw()

        self.visualizer.draw()

    def find_visualizer_class(self, vis_name):
        return list(filter(lambda x: x[0] == vis_name, visualizers))[0][1]

    def change_visualizer(self, vis_name)   :
        print('Changing visualizer: %s ' % vis_name)
        rect = self.get_visualizer_rect()
        self.visualizer = self.find_visualizer_class(vis_name)(rect)
