import RPi.GPIO as GPIO

class RGB:
    def __init__(self, red_pin: int, green_pin: int, blue_pin: int):
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(red_pin, GPIO.OUT)
        self._red_pwm = GPIO.PWM(red_pin, 2000)
        self._red_pwm.start(0)

        GPIO.setup(green_pin, GPIO.OUT)
        self._green_pwm = GPIO.PWM(green_pin, 2000)
        self._green_pwm.start(0)

        GPIO.setup(blue_pin, GPIO.OUT)
        self._blue_pwm = GPIO.PWM(blue_pin, 2000)
        self._blue_pwm.start(0)

    def __del__(self):
        self._red_pwm.stop()
        self._green_pwm.stop()
        self._blue_pwm.stop()

    def set_color(self, r: float, g: float, b: float):
        self._red_pwm.ChangeDutyCycle(r)
        self._green_pwm.ChangeDutyCycle(g)
        self._blue_pwm.ChangeDutyCycle(b)
