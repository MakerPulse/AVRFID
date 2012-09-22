int LOAD = 0;
int EDIT = 1;
int ADD = 2;
int SEARCH = 3;
int CANCEL = 4;
int SERIAL = 5;
int UP = 6;
int DOWN = 7;

import processing.serial.*;
Serial myPort;
int port;

PFont font;
color textColor = #FFFFFF;
color normalColor = #555555;
color hoverColor = #444444;
color clickColor = #111111;
int buttonWidth = 100;
int buttonHeight = 50;

button[] buttons = {new button("load", 000, 24),
                    new button("edit", 100, 24),
                    new button("add", 200, 24),
                    new button("search", 300, 24),
                    new button("cancel", 400, 24),
                    new button("serial", 500, 24),
                    new button("^", 582, 193, 18, 18),
                    new button("v", 582, 408, 18, 18)};
                    
ArrayList people;
ArrayList present;
String[] lines;

String date = "01/01/2012";

String inputText = "";
String fileName = "";
String message1 = "Open Serial port to begin scanning";
String message2 = "Open Names file to load tags";
String message3 = "Welcome to RPI ID Reader";
String message4 = "";

int currentEntry = 3;

String namesFile = "";
String inRfid = null;
String inString = null;

boolean fileOpen = false;
boolean portOpen = false;

void message(String output){
  message4 = message3;
  message3 = message2;
  message2 = message1;
  message1 = output;
}

void keyPressed(){
  if(key == 8){  //backspace
    if(inputText.length() != 0)
      inputText = inputText.substring(0, inputText.length()-1);
  }
  else if(32 <= key && key <= 126){
    inputText += key;
  }
  else if(key == 10 || key == 13){
    inputText += key;
  }
}

void serialEvent(Serial p){
  inString = p.readString();
  if(inString != null){
    println(inString);
    inString = inString.substring(0,11);
    if((currentEntry = search(inString)) < 0){
      message("rfid \"" + inString + "\" not found in file");
      currentEntry = 0;
    }
    else{
      message("rfid \"" + inString + "\" found at entry " + currentEntry);
    }
  }
}

String getText(){
  if(inputText.length() > 0 && inputText.charAt(inputText.length()-1) == 10)
    return(inputText.substring(0, inputText.length()-1));
  else
    return "";
}

int search(String searchFor){
  person tperson;
  for(int i=0; i<people.size(); i++){
    tperson = (person) people.get(i);
    if(tperson.email.equals(searchFor) || 
       tperson.name.equals(searchFor) || 
       tperson.rfid.equals(searchFor)){      //if we found it
      return i;
    }
  }
  return -1;
}

void setup(){
  size(600, 450);
  font = loadFont("CourierNewPS-BoldMT-12.vlw");
  textFont(font, 15);
  date = month() + "/" + day() + "/" + year();
  prepareExitHandler();
  people = new ArrayList();
}

void draw(){
  background(0);
  //nostroke();
  
  //this highlights buttons when the mouse hovers over them, or clicks on them
  for(int i=0; i<buttons.length; i++){
    if(mouseX > buttons[i].xpos && mouseX < buttons[i].xpos+buttons[i].xdim &&                  //over the button widthwise
       mouseY > buttons[i].ypos && mouseY < buttons[i].ypos+buttons[i].ydim){           //over the button heightwise
      if(mousePressed){
        fill(clickColor);
        buttons[i].clicked = true;
      }
      else
        fill(hoverColor);
    }
    else
      fill(normalColor);
    rect(buttons[i].xpos, buttons[i].ypos, buttons[i].xdim, buttons[i].ydim);
  }
  
  //these are small divisions in the screen which separates messages from input text, and input text from list
  fill(#444444);
  rect(0, 166, 600, 3);
  rect(0, 190, 600, 3);
  rect(0, 426, 600, 3);
  
  //general text printing
  fill(textColor);
  textFont(font, 15);
  textAlign(CENTER);
  text("Press cancel at any time to return", 300, 445);
  textAlign(LEFT);
  text(date, 5, 15);                  //date in upper left
  text(message4, 5, 86);              //output messages to user
  text(message3, 5, 110);
  text(message2, 5, 134);
  text(message1, 5, 158);
  text(inputText, 5, 172, 595, 100);  //input text field  
  
  //for debug
  text(mouseX, 5, 445);
  text(mouseY, 45, 445);
  
  //button name text
  textAlign(CENTER);
  for(int i=0; i<buttons.length; i++){
    text(buttons[i].name, buttons[i].xpos+buttons[i].xdim/2, buttons[i].ypos+buttons[i].ydim/2+4);
  }  
  
  //open the people file
  if(buttons[LOAD].clicked){
    fileName = selectInput();
    if(loadStrings(fileName) != null){ //load the file
      lines = loadStrings(fileName);
      //println(fileName);
      //println(lines.length);
      fileOpen = true;
      currentEntry = 0;
      message("file \"" + fileName.substring(fileName.lastIndexOf('\\')+1) + "\" opened");
      for(int i=1; i<lines.length; i++){    //first line is a header
        String tstring[] = split(lines[i], ',');    
        people.add(new person(tstring[1], tstring[2], tstring[3], tstring[4]));
      }
    }
    else{
      fileOpen = false;
      message("invalid file");
    }
    buttons[LOAD].clicked = false;
    mousePressed = false;
  }
  
  if(buttons[SERIAL].clicked){              //open/refresh serial port
    if(portOpen){                          //close open port
      myPort.stop();
      myPort.clear();
      portOpen = false;
    }
    String message = "Ports: ";
    for(int i=0; i<Serial.list().length; i++){
      message += i;     //list each one with the corresponding user input to select
      message += ": ";
      message += Serial.list()[i];
      message += ", ";
    }
    message += "please select port";
    if(message1.charAt(0) != 'P')
      message(message);
      
    if(getText() != ""){
      port = getText().charAt(0)-48;
      myPort = new Serial(this, Serial.list()[port], 9600);
      portOpen = true;
      buttons[SERIAL].clicked = false;
      message("port opened");
      myPort.bufferUntil(10);
      inputText = "";
    }
  }
  
  if(buttons[UP].clicked){              //scroll list up
    buttons[UP].clicked = false;
    //mousePressed = false;
    currentEntry--;
    if(currentEntry < 0)
      currentEntry = 0;
  }
  
  if(buttons[DOWN].clicked){            //scroll list down
    buttons[DOWN].clicked = false;
    //mousePressed = false;
    currentEntry++;
    if(currentEntry >= people.size())
      currentEntry--;
  }
  
  if(buttons[ADD].clicked && fileOpen){            //add new person
    if(message1.charAt(0) != 'E'){
      message("Enter \'First Last,email,role\'");
    }
    if(getText() != ""){
      String tstring[] = split(getText(), ',');
      people.add(new person(tstring[0], tstring[1], "0000000000", tstring[2]));
      buttons[ADD].clicked = false;
      inputText = "";
      message("New person added successfully");
    }
  }
  
  if(buttons[SEARCH].clicked){
    person tperson;
    textAlign(LEFT);
    if(message1 != "Input string to search for:")
      message("Input string to search for:");
    if(getText() != ""){
      if((currentEntry = search(getText())) < 0){
        message("string \"" + getText() + "\" not found in file");
        currentEntry = 0;
      }
      else{
        message("string \"" + getText() + "\" found at entry " + currentEntry);
      }
      buttons[SEARCH].clicked = false;
      inputText = "";
    }
  }
  
  if(buttons[CANCEL].clicked){
    buttons[SEARCH].clicked = false;
    buttons[LOAD].clicked = false;
    buttons[EDIT].clicked = false;
    buttons[ADD].clicked = false;
    buttons[SERIAL].clicked = false;
    buttons[CANCEL].clicked = false;
  }
  
  if(fileOpen){                         //print a list of entries
    textAlign(RIGHT);
    text(fileName.substring(fileName.lastIndexOf('\\')+1), 595, 15);
    textAlign(LEFT);
    person tperson = (person) people.get(0);
    text("Name", 5, 206);             //header of file
    text("RCSID", 200, 206);
    text("RFID", 300, 206);
    text("Role", 440, 206);
    for(int i=0; i<9; i++){
      if(i+currentEntry >= people.size())
        break;
      tperson = (person) people.get(i+currentEntry);
      text(tperson.name, 5, 230+i*24);
      text(tperson.email, 200, 230+i*24);
      text(tperson.rfid, 300, 230+i*24);
      text(tperson.role, 440, 230+i*24);
    }
  }
  
  if(portOpen){
    textAlign(LEFT);
    text(Serial.list()[port], 350, 15);
  }
  
  if(!fileOpen || !portOpen){              //port must be open and file loaded
    fill(#FF0000);
    textAlign(LEFT);
    text("NOT OK to scan", 150, 15);
  }
  
  else{                                    //if the port is open and the file is loaded
    fill(#00FF00);
    textAlign(LEFT);
    text("OK to scan", 150, 15);
  }
}

class button{                              //class to group the buttons together
  int xpos;
  int ypos;
  int xdim;
  int ydim;
  String name;
  boolean clicked;
  
  button(String s, int x, int y){          //create a button at x,y called s
    xpos = x;
    ypos = y;
    xdim = buttonWidth;
    ydim = buttonHeight;
    name = s;
  }
  
  button(String s, int x, int y, int xd, int yd){    //create a button at x,y called s with dimensions xd and yd
    xpos = x;
    ypos = y;
    xdim = xd;
    ydim = yd;
    name = s;
  }
}

class person{                        //class to list people
  //all attributes are public in processing unless specified otherwise by 'private'
  String name;                          //person's first and last name
  String email;                         //rpi student email, up to @
  String rfid;                          //rpi student id card rfid number
  public String role;                   //officer, member, associate, advisor
  
  person(String n){                  //create a person with a name only
    name = n;
    email = "";                          //blank RCSID
    rfid = "";                           //blank RFID
    role = "associate";                  //associate
  }
  
  person(String n, String e, String r){//create person with name, email, and rfid
    name = n;
    email = e;
    rfid = r;              
    role = "associate";               //change role as needed after addition
  }
  
  person(String n, String e, String r, String q){//create person with name, email, rfid, and role
    name = n;
    email = e;
    rfid = r;              
    role = q;
  }
}

private void prepareExitHandler(){
  Runtime.getRuntime().addShutdownHook(new Thread(new Runnable(){
    public void run(){
      System.out.println("SHUTDOWN HOOK");
      // application exit code here
      if(fileOpen){          
        saveStrings(fileName, lines);
        System.out.println("file saved successfully");
      }
    }
  }));
}


