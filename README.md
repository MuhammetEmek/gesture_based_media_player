# Gesture Based Media Player

In this project, here we mainly intend to detect human gesture recognizing by camera; controlling some functions such as start, stop, voice control. Hand gestures are the main detection point here and it needs to be done quite sensitive and critical. Finger position and hand position in space as two intersecting planes is critical for determination of move.

# Tools & Techniques

* Python (3.8)
* Mediapipe (https://google.github.io/mediapipe/solutions/hands)
* PyQt5     (https://pypi.org/project/PyQt5/)
* OpenCV    (https://opencv.org/)
* sys
* numpy

# Description

I used the library named MediaPipe which employs machine learning (ML) to infer 21 3D landmarks of a hand. MediaPipe Hands utilizes an ML pipeline consisting of multiple models working together: A palm detection model that operates on the full image and returns an oriented hand bounding box. A hand landmark model that operates on the cropped image region defined by the palm detector and returns high-fidelity 3D hand keypoints. From the images obtained from the camera, the following 21 point coordinates are reached. Then, the 5 movements mentioned above are tried to be determined according to the horizontal and vertical positions of these points with each other.

![Hand_Landmarks](https://github.com/MuhammetEmek/gesture_based_media_player/blob/main/screenshots/hand_landmarks.png)

As shown in the following illustration; the camera and video output divides the process parts, right hand side shows the video and left hand side shows the camera output with detected gesture action and the volume slider. Video output has the media’s name and the button showing the play and stop cases. Media slider is also available in the process.

![Application](https://github.com/MuhammetEmek/gesture_based_media_player/blob/main/screenshots/Application.png)

According to the hand motions, media player takes action with 5 moves. Apart from these 5 moves, the action won’t be taken into consideration. 
These moves are;
* Stop; all fingers are bare open and upward direction
* Start; all fingers closed
* Volume up; only thumbs up other fingers are closed
* Volume down; only thumbs down other fingers are closed
* Volume mute; 2 fingers as forefinger and middle finger in upward direction other fingers are closed
* In case which no hands are determined, no hands case occurs.

As can be seen in following illustration, the video captures the position of the hand, later it detects the gesture position by 21 point coordinates case. While identifying the hand position, there are several point detectors available in coordinate positioning. 5 actions are taught and also voice detection is available in this case

![Workflow](https://github.com/MuhammetEmek/gesture_based_media_player/blob/main/screenshots/Workflow.png)

Below are the some screenshots of the application for different hand gestures.

![Play](https://github.com/MuhammetEmek/gesture_based_media_player/blob/main/screenshots/Play.png)

![VolumeUp](https://github.com/MuhammetEmek/gesture_based_media_player/blob/main/screenshots/VolumeUp.png)

![VolumeDown](https://github.com/MuhammetEmek/gesture_based_media_player/blob/main/screenshots/VolumeDown.png)
