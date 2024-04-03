import cv2
from gtts import gTTS
import os
from kivy.graphics.texture import Texture  # Import Texture class from Kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from ultralytics import YOLO
import time


# Load YOLOv5 model
model = YOLO('best.pt')

class ObjectDetectionApp(App):
    def build(self):
        self.detected_objects = []
        self.cap = cv2.VideoCapture(0)  # Open camera

        
        # Create the layout
        layout = BoxLayout(orientation='vertical')
        
        # Create the image widget to display the camera feed
        self.image_widget = Image()
        layout.add_widget(self.image_widget)

        # Create buttons for modes
        crossing_street_button = Button(text='Crossing street mode')
        crossing_street_button.bind(on_press=self.start_crossing_street_mode)
        free_walking_button = Button(text='Free walking mode')
        free_walking_button.bind(on_press=self.start_free_walking_mode)
        
        layout.add_widget(crossing_street_button)
        layout.add_widget(free_walking_button)
        return layout


    def start_crossing_street_mode(self, instance):
        self.stop_free_walking_mode()  # Stop free walking mode if running
        self.crossing_street_clock_event = Clock.schedule_interval(self.crossing_street_mode, 1.0/30.0)

    def start_free_walking_mode(self, instance):
        self.stop_crossing_street_mode()  # Stop crossing street mode if running
        self.free_walking_clock_event = Clock.schedule_interval(self.free_walking_mode, 1.0/30.0)

    def stop_crossing_street_mode(self):
        if hasattr(self, 'crossing_street_clock_event'):
            self.crossing_street_clock_event.cancel()

    def stop_free_walking_mode(self):
        if hasattr(self, 'free_walking_clock_event'):
            self.free_walking_clock_event.cancel()

################################################ CROSSIG THE STREET ######################################################################3

    def crossing_street_mode(self, dt):
        ret, frame = self.cap.read()  # Read frame from camera
        if not ret:
            return
        self.detected_objects.clear()  # Clear the list of detected objects
        results = model(frame)
        for result in results:
            for c in result.boxes.cls:
                text_en = model.names[int(c)]
                self.detected_objects.append(text_en)

        # Check conditions for speaking in Crossing street mode
        if "crosswalk" in self.detected_objects or "green-traffic-light" in self.detected_objects and "car" not in self.detected_objects:
            speech = gTTS(text=" خط مشاة يمكنك العبور ", lang='ar', slow=False)

        elif "crosswalk" in self.detected_objects and "green-traffic-light" in self.detected_objects and "car" in self.detected_objects:
            speech = gTTS(text="امامك سيارة انتظر ", lang='ar', slow=False)

        elif "car" in self.detected_objects:
            speech = gTTS(text="امامك سياره لا تعبر ", lang='ar', slow=False)

        elif "red traffic light" in self.detected_objects:
            speech = gTTS(text="الاشارة حمراء لا تعبر  ", lang='ar', slow=False)

        elif "red traffic light" in self.detected_objects and  "crosswalk" in self.detected_objects:
            speech = gTTS(text=" يوجد خط مشاة الاشارة حمراء لا تعبر  ", lang='ar', slow=False)

        elif "yellow-traffic-light" in self.detected_objects:
            speech = gTTS(text="الاشارة صفراء انتظر   ", lang='ar', slow=False)
        else:
            speech = gTTS(text="يمكنك عبور الطريق", lang='ar', slow=False)

        speech.save("output.mp3")
        os.system("start output.mp3")
        time.sleep(5)
        # Display the camera feed
        self.image_widget.texture = self.cv2_to_kivy_texture(frame)


################################################THE END OF CROSSIG THE STREET ######################################################################3

############################################## FREE WALKING #############################################################################     

    def free_walking_mode(self, dt):

        ret, frame = self.cap.read()  # Read frame from camera
        if not ret:
            return

        self.detected_objects.clear()  # Clear the list of detected objects

        results = model(frame)
        for result in results:
            for c in result.boxes.cls:
                text_en = model.names[int(c)]
                self.detected_objects.append(text_en)

        # Check conditions for speaking in Free walking mode
        if "barrier" in self.detected_objects or "pothole" in self.detected_objects or "traffic-cones" in self.detected_objects or "tree" in self.detected_objects :
            speech = gTTS(text="انتبه امامك عقبه", lang='ar', slow=False)
        else:
            speech = gTTS(text="يمكنك المشي", lang='ar', slow=False)    
        speech.save("output.mp3")
        os.system("start output.mp3")
        time.sleep(5)

        # Display the camera feed
        self.image_widget.texture = self.cv2_to_kivy_texture(frame)

    def cv2_to_kivy_texture(self, frame):
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture
    
############################################## THE END OF FREE WALKING #############################################################################     


if __name__ == '__main__':
    ObjectDetectionApp().run()
