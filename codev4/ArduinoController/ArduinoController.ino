#define dir 3
#define step 4

#define UP1 A5
#define DW1 A4
#define UP2 A2    //công tắc hành trình TRÊN cấp xoài
#define DW2 A3    //công tắc hành trình DƯỚI cấp xoài
#define UP3 A1    //công tắc hành trình TRÊN xylanh đẩy xoài ra ngoài
#define DW3 A0    //công tắc hành trình DƯỚI xylanh đẩy xoài ra ngoài
#define SENSOR 2  //cảm biến tiệm cận

#define IN1 5  //xylanh đo phổ
#define IN2 6  //xylanh đo phổ
#define R3 7   //xylanh đẩy xoài ra ngoài
#define L3 8   //xylanh đẩy xoài ra ngoài
#define R2 10  //xylanh cấp xoài
#define L2 9   //xylanh cấp xoài
#define R5 13  //băng tải phân loại xoài
#define R6 11  //động cơ giảm tốc lăn xoài trong bường chụp
#define R4 12  //băng tải cấp xoài

int incomingByte;
unsigned int speed = 125;  //tốc độ xoay xoài
bool continueRot = false;

//động cơ bước
char currentPosition = 'B';
char newPosition;

int stepState = LOW;
bool next = false;
bool firsttime2 = true;
unsigned long previousMillis = 0;
const long interval = 1;  //to do gat phan loai
unsigned long count = 0;
unsigned long stepsupply = 900;

//xylanh
bool back = false;
bool done = false;
bool start = false;

bool back1 = false;
bool done1 = false;

bool back2 = false;
bool done2 = false;

//bang tai cap xoai
bool pass = false;
unsigned long previousMillis0 = 0;
const long interval0 = 4000;  //thoi gian cho xoai cham
bool firsttime3 = true;

//dong co xoay xoai
bool pass1 = false;


//bang tai phan loai
bool firsttime1 = true;
bool onbangtai = false;
unsigned long previousMillis1 = 0;
const long interval1 = 10000;  //thoi gian bang tai phan loai dung

//xylanh2
unsigned long previousMillis2 = 0;
const long interval2 = 3000;  //thoi gian do pho
bool firsttime = true;

bool STOP = false;

void setup() {
  Serial.begin(115200);

  pinMode(step, OUTPUT);
  pinMode(dir, OUTPUT);
  pinMode(R2, OUTPUT);
  pinMode(L2, OUTPUT);
  pinMode(R3, OUTPUT);
  pinMode(L3, OUTPUT);
  pinMode(R4, OUTPUT);
  pinMode(R5, OUTPUT);
  pinMode(R6, OUTPUT);

  pinMode(UP2, INPUT);
  pinMode(DW2, INPUT);
  pinMode(UP3, INPUT);
  pinMode(DW3, INPUT);
  pinMode(SENSOR, INPUT);

  //cho xylanh 1 chạm công tắc hành trình trên
  while (digitalRead(UP2) != 1) {
    digitalWrite(R2, 0);
    digitalWrite(L2, 1);
  }
  digitalWrite(R2, 0);
  digitalWrite(L2, 0);

  //cho xylanh 2 chạm công tắc hành trình dưới
  while (digitalRead(DW3) != 1) {
    digitalWrite(R3, 1);
    digitalWrite(L3, 0);
  }
  digitalWrite(R3, 0);
  digitalWrite(L3, 0);

  //cho xylanh 3 chạm công tắc hành trình dưới
  while (digitalRead(DW1) != 1) {
    digitalWrite(IN1, 0);
    digitalWrite(IN2, 1);
  }
  digitalWrite(IN1, 0);
  digitalWrite(IN2, 0);

  //dừng động cơ bước
  digitalWrite(dir, 0);
  digitalWrite(step, stepState);

  //dừng động cơ
  digitalWrite(R6, 0);

  //dừng băng tải cấp xoài
  digitalWrite(R4, 0);

  //dừng băng tải phân loại
  digitalWrite(R5, 0);

  //gửi lệnh kết nối cho máy
  Serial.println("Y");
  delay(100);
}

void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
  }
  if (STOP == false) {
    Bangtai_capxoai();
    Xylanh1();
    Xoay();
    // Xylanh3();
  }
  Step();
  Xylanh2();
  Bangtai_phanloai();
}

//Dieu khien xoay xoai=========================================================================================================
void Xoay() {
  if (incomingByte == 'Q' && pass1 == false) {
    analogWrite(R6, 255);
    pass = false;
  }
  if (incomingByte == 'W' && pass1 == false) {
    analogWrite(R6, speed);
  }
  if (incomingByte == 'E' && pass1 == false) {
    digitalWrite(R6, 0);
  }
}

//Dieu khien bang tai cap xoai==================================================================================================
void Bangtai_capxoai() {
  if (digitalRead(SENSOR) == 1 && pass == false) {
    digitalWrite(R4, 1);
  }
  if (digitalRead(SENSOR) == 0 && pass == false) {
    digitalWrite(R4, 0);
  }
  if (incomingByte == 'H' && digitalRead(SENSOR)==0){
    pass = true;
    digitalWrite(R4,1);
    unsigned long currentMillis0 = millis();
    if (firsttime3){
      previousMillis0 = currentMillis0;
      firsttime3 = false;
    }
    if (currentMillis0 - previousMillis0 >= interval0){
      start = true;
      pass = false;
      done = false;
    }
  }
}

//Dieu khien xylanh cap xoai====================================================================================================
void Xylanh1() {
  if (start == true) {
    if (back == false && done == false && digitalRead(SENSOR) == 0 && digitalRead(DW3) == 1) {
      digitalWrite(R2, 1);
      digitalWrite(L2, 0);
      start = false;
    }
  }
  if (digitalRead(DW2) == 1) {
    digitalWrite(R2, 0);
    digitalWrite(L2, 0);
    back = true;
  }
  if (back == true) {
    digitalWrite(R2, 0);
    digitalWrite(L2, 1);
    // digitalWrite(R4, 0);
    done = true;
    firsttime3 = true;
  }
  if (digitalRead(UP2) == 1) {
    digitalWrite(R2, 0);
    digitalWrite(L2, 0);
    back = false;
  }
}

//dieu khien xylanh do pho============================================================================================
void Xylanh3() {
  if (incomingByte == 'K') {
    if (back2 == false && done2 == false) {
      analogWrite(R6, 0);
      digitalWrite(IN1, 1);
      digitalWrite(IN2, 0);
    }
  }
  if (digitalRead(UP1) == 1) {
    unsigned long currentMillis2 = millis();
    if (firsttime) {
      previousMillis2 = currentMillis2;
      firsttime = false;
    }
    if (currentMillis2 - previousMillis2 >= interval2) {
      back2 = true;
    } else {
      digitalWrite(IN1, 0);
      digitalWrite(IN2, 0);
    }
  }
  if (back2 == true) {
    digitalWrite(IN1, 0);
    digitalWrite(IN2, 1);
    done2 = true;
    continueRot = true;
  }
  if (digitalRead(DW1) == 1) {
    digitalWrite(IN1, 0);
    digitalWrite(IN2, 0);
    if (continueRot) {
      analogWrite(R6, speed);
      continueRot = false;
    }
    back2 = false;
    firsttime = true;
  }
  if (incomingByte != 'K') {
    done2 = false;
  }
}

//Dieu khien dong co phan loai==================================================================================================
void Step() {
  if (incomingByte == 'A' || incomingByte == 'B') {
    newPosition = incomingByte;
    next = false;
  }
  if (newPosition == 'A' && newPosition != currentPosition && currentPosition == 'B') {
    unsigned long currentMillis = millis();
    if (firsttime2) {
      previousMillis = currentMillis;
      firsttime2 = false;
      STOP = true;
    }
    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis;

      if (stepState == LOW) {
        stepState = HIGH;
      } else {
        stepState = LOW;
      }
      digitalWrite(dir, 0);
      digitalWrite(step, stepState);
      count += 1;
    }
    if (count == stepsupply) {
      currentPosition = newPosition;
      count = 0;
      next = true;
      STOP = false;
    }
  }

  if (newPosition == 'B' && newPosition != currentPosition && currentPosition == 'A') {
    unsigned long currentMillis = millis();
    if (firsttime2) {
      previousMillis = currentMillis;
      firsttime2 = false;
      STOP = true;
    }
    if (currentMillis - previousMillis >= interval) {
      previousMillis = currentMillis;

      if (stepState == LOW) {
        stepState = HIGH;
      } else {
        stepState = LOW;
      }
      digitalWrite(dir, 1);
      digitalWrite(step, stepState);
      count += 1;
    }
    if (count == stepsupply) {
      currentPosition = newPosition;
      count = 0;
      next = true;
      STOP = false;
    }
  }
  if (incomingByte == 'A' && incomingByte == currentPosition || incomingByte == 'B' && incomingByte == currentPosition) {
    next = true;
  }
}

//dieu khien xylanh day xoai ra ngoai============================================================================================
void Xylanh2() {
  if (back1 == false && done1 == false && next == true) {
    digitalWrite(R3, 0);
    digitalWrite(L3, 1);
    digitalWrite(R4, 0);
    pass1 = true;
    digitalWrite(R6, 0);
  }
  if (digitalRead(UP3) == 1) {
    digitalWrite(R3, 0);
    digitalWrite(L3, 0);
    back1 = true;
    firsttime1 = true;
    firsttime2 = true;
    onbangtai = true;
  }
  if (back1 == true) {
    digitalWrite(R3, 1);
    digitalWrite(L3, 0);
    done1 = true;
  }
  if (digitalRead(DW3) == 1) {
    digitalWrite(R3, 0);
    digitalWrite(L3, 0);
    back1 = false;
    if (done1) {
      next = false;
      pass1 = false;
    }
  }
  if (incomingByte == 'H') {
    done1 = false;
  }
}

void Bangtai_phanloai() {
  if (onbangtai) {
    unsigned long currentMillis1 = millis();
    if (firsttime1) {
      previousMillis1 = currentMillis1;
      firsttime1 = false;
    }
    if (currentMillis1 - previousMillis1 >= interval1) {
      digitalWrite(R5, 0);
      onbangtai = false;
    } else {
      digitalWrite(R5, 1);
    }
  }
}
