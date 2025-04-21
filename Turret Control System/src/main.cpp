#include <Arduino.h>
#include <AccelStepper.h>
#include <Servo.h>

// Motor setup: DRIVER mode, STEP and DIR pins
AccelStepper stepperX(AccelStepper::DRIVER, 3, 2);  // X-axis (pan)
AccelStepper stepperY(AccelStepper::DRIVER, 5, 4);  // Y-axis (tilt)

// Servo
Servo triggerServo;
const int SERVO_PIN = 9;
const int SERVO_FIRE_ANGLE = 90;
const int SERVO_REST_ANGLE = 0;

void setup() {
  Serial.begin(115200);

  // Configure X-axis motor
  stepperX.setMaxSpeed(1000);     // Max steps/sec
  stepperX.setAcceleration(300);  // Smoother movement

  // Configure Y-axis motor
  stepperY.setMaxSpeed(800);      // Less speed if lower microstepping
  stepperY.setAcceleration(250);

  // Configure servo
  triggerServo.attach(SERVO_PIN);
  triggerServo.write(SERVO_REST_ANGLE);

}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    int first = input.indexOf(',');
    int second = input.indexOf(',', first + 1);

    if (first > 0 && second > first) {
      int xSpeed = input.substring(0, first).toInt();
      int ySpeed = input.substring(first + 1, second).toInt();
      int fire = input.substring(second + 1).toInt();

      stepperX.setSpeed(xSpeed);
      stepperY.setSpeed(ySpeed);

      // Fire toggle
      if (fire == 1) {
        triggerServo.write(SERVO_FIRE_ANGLE);
      } else {
        triggerServo.write(SERVO_REST_ANGLE);
      }
    }
  }

  stepperX.runSpeed();
  stepperY.runSpeed();
}


// // Define pins
// const int stepPin = 3;       // PUL+
// const int dirPin = 2;        // DIR+
// const int stepsPerRevolution = 2000; // Microsteps per full revolution

// // Acceleration parameters
// const int defaultMinDelay = 200;    // Default minimum delay in microseconds (max speed)
// const int defaultMaxDelay = 2000;   // Default maximum delay in microseconds (start speed)
// const int accelSteps = 200;  // Number of steps to accelerate or decelerate

// void stepMotorWithAccelerationAndSpeed(int steps, bool clockwise, int speedPercentage) {
//   // Calculate delays based on speed percentage
//   int minDelay = defaultMinDelay + (100 - speedPercentage) * (defaultMaxDelay - defaultMinDelay) / 100;
//   int maxDelay = defaultMaxDelay;
//   int delayTime = maxDelay; // Start with the maximum delay
//   int stepIncrement = (maxDelay - minDelay) / accelSteps; // Calculate delay decrement per step

//   // Set direction
//   digitalWrite(dirPin, clockwise ? HIGH : LOW);

//   // Accelerate
//   for (int i = 0; i < accelSteps && i < steps; i++) {
//     digitalWrite(stepPin, HIGH);
//     delayMicroseconds(delayTime);
//     digitalWrite(stepPin, LOW);
//     delayMicroseconds(delayTime);
//     delayTime = max(delayTime - stepIncrement, minDelay); // Decrease delay
//   }

//   // Constant speed
//   for (int i = accelSteps; i < steps - accelSteps; i++) {
//     digitalWrite(stepPin, HIGH);
//     delayMicroseconds(minDelay);
//     digitalWrite(stepPin, LOW);
//     delayMicroseconds(minDelay);
//   }

//   // Decelerate
//   for (int i = 0; i < accelSteps && i < steps; i++) {
//     digitalWrite(stepPin, HIGH);
//     delayMicroseconds(delayTime);
//     digitalWrite(stepPin, LOW);
//     delayMicroseconds(delayTime);
//     delayTime = min(delayTime + stepIncrement, maxDelay); // Increase delay
//   }
// }

// void setup() {
//   pinMode(stepPin, OUTPUT);
//   pinMode(dirPin, OUTPUT);

//   // Set initial direction
//   digitalWrite(dirPin, HIGH);  // HIGH or LOW changes direction
// }

// void loop() {
//   // Rotate one full revolution clockwise with acceleration and speed control (50% speed)
//   stepMotorWithAccelerationAndSpeed(stepsPerRevolution, true, 90);
//   delay(1000);

//   // Rotate one full revolution counter-clockwise with acceleration and speed control (75% speed)
//   stepMotorWithAccelerationAndSpeed(stepsPerRevolution, false, 90);
//   delay(1000);
// }