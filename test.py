#imports
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, FadeTransition, FallOutTransition, RiseInTransition
from kivy.clock import Clock
import time
from kivy.animation import Animation

# behiaviours
from kivy.uix.behaviors import ButtonBehavior

# properties
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.properties import NumericProperty

# Layouts
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout

# widgets
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel
from kivy.uix.video import Video
from kivy.uix.image import Image



# enter Window.fullscreen = 'auto' to go to fullscreen mode
# from kivy.core.window import Window
# Window.fullscreen = 'auto'

Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '400')


# Main Data classes
class Theme:
    def __init__(self, type, source, font):
        self.type = type  # can be image | video | blank
        self.source = source
        self.font = font

class DataClass(object):
    themes = []
    themes.append(Theme('video','./assets/videos/1.mp4', './fonts/1.ttf'))
    themes.append(Theme('image', './assets/images/1.jpg', './fonts/2.ttf'))
    themes.append(Theme('blank', '', './fonts/5.ttf'))

    quoteString = '“Everybody is a genius. But if you judge a fish by its ability to climb a tree, it will live its whole life believing that it is stupid.” — Albert Einstein'
    fontSize = 60

    def getString():
        return DataClass.quoteString


# Loading Screen
class LoadingScreen(Screen):
    
    def __init__(self,**kwargs):
        super(LoadingScreen, self).__init__(**kwargs)
    
    def on_enter(self, *args):
        self.displayScreenThenLeave()
    
    def displayScreenThenLeave(self):
        #schedued after 3 seconds
        Clock.schedule_once(self.changeScreen, 2.3)

    def changeScreen(self, *args):
        #now switch to main screen
        self.parent.transition = RiseInTransition()
        self.parent.current = "home_screen"
    
# loading spinner
class LoadingSpinner(FloatLayout):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super(LoadingSpinner, self).__init__(**kwargs)
        anim = Animation(angle = -360, duration=1) 
        anim += Animation(angle = -360, duration=1)
        anim.repeat = True
        anim.start(self)

    def on_angle(self, item, angle):
        if angle == -360:
            item.angle = 0

# carousel
class HomeScreen(Screen):
    pass

# Overlay section
class MenuBar(AnchorLayout):

    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        self.button = MenuButton()
        self.showMenu = True;
        self.add_widget(self.button)
        self.event = Clock.schedule_once(self.hide, 3)

    def toggleMenu(self):
        print('toggle clicked')
        if(self.showMenu == True):
            self.hide()
        else:
            self.show()

    
    def show(self):
        self.showMenu = True
        entryAnim = Animation(size_hint=(0.05,0.15), opacity=1, duration=0.2)
        entryAnim.start(self.button)
        self.event()

    def hide(self, *largs):
        self.showMenu = False
        exitAnim = Animation(size_hint=(0,0), opacity=0, duration=0.2)
        exitAnim.start(self.button)
        self.event.cancel()

        

class MenuButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.size_hint = (0.05,0.15)
        self.padding = 5
        image = Image(source='./assets/icons/menu.png', height=60, width=60)
        self.add_widget(image)
    
    def on_press(self):
        print('clicked')
        self.parent.parent.parent.transition = FadeTransition()
        self.parent.parent.parent.current = "settings_screen"


class SlideComponent(BoxLayout):
    def __init__(self, **kwargs):
        super(SlideComponent, self).__init__(**kwargs)
        
        carousel = Carousel(direction='right')
        for idx, i in enumerate(DataClass.themes):
            if(i.type == 'blank'):
                theme = BlankTheme()
                carousel.add_widget(theme, idx)
            elif(i.type == 'video'):
                theme = VideoTheme()
                carousel.add_widget(theme, idx)
            elif(i.type == 'image'):
                theme = ImageTheme()
                carousel.add_widget(theme, idx)
        self.add_widget(carousel)

    def handleSlideClick(self):
        self.mbr.toggleMenu()

class BlankTheme(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super(BlankTheme, self).__init__(**kwargs)
        layout = BoxLayout(width= 1280, height= 400, padding= [40,60,40,60])
        label = Label(text=DataClass.quoteString, font_size=DataClass.fontSize, font_name="./fonts/1.ttf",  color= [1,1,1,1], text_size= [1240,360], halign= 'center', valign= 'middle')
        layout.add_widget(label)
        self.add_widget(layout)
    
    def on_press(self):
        self.parent.parent.parent.handleSlideClick()

class VideoTheme(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super(VideoTheme, self).__init__(**kwargs)
        video = Video(source="./assets/videos/1.mp4", play="True", options= {'eos': 'loop'}, height= 400, width= 1280)
        self.add_widget(video)
        
        layout = BoxLayout(width= 1280, height= 400, padding= [40,60,40,60], orientation= 'vertical')
        label = ShadowLabel(text= DataClass.quoteString, font_size= DataClass.fontSize, font_name="./fonts/5.ttf", tint= [.5, .5, .5, .5], color= [1,1,1,1], bold= True, text_size= [1240,360], halign= 'center', valign= 'middle', decal= [2, 0])
        layout.add_widget(label)
        self.add_widget(layout)
    
    def on_press(self):
        self.parent.parent.parent.handleSlideClick()

class ImageTheme(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super(ImageTheme, self).__init__(**kwargs)
        image = Image(source="./assets/images/1.jpg", height= 400, width= 1280)
        self.add_widget(image)
        
        layout = BoxLayout(width= 1280, height= 400, padding= [40,60,40,60], orientation= 'vertical')
        label = ShadowLabel(text= DataClass.quoteString, font_size= DataClass.fontSize, font_name="./fonts/7.otf", tint= [.5, .5, .5, .5], color= [1,1,1,1], bold= True, text_size= [1240,360], halign= 'center', valign= 'middle', decal= [2, 0])
        layout.add_widget(label)
        self.add_widget(layout)
    
    def on_press(self):
        self.parent.parent.parent.handleSlideClick()

# Settings screen
class SettingsScreen(Screen):
    def __init__(self,**kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    def goToHome(self):
        self.parent.current = "home_screen"



# Window Manager
class WindowManager(ScreenManager):
    pass

# Shadow Label Component
class ShadowLabel(Label):
    decal = ListProperty([0, 0])
    tint = ListProperty([1, 1, 1, 1])


# main app render
kv = Builder.load_file('main.kv')

class MainApp(App):
    def build(self):
        return kv

if __name__ == "__main__":
    MainApp().run()