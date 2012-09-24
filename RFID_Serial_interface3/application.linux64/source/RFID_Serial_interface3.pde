int LOAD = 0;
int EDIT = 1;
int ADD = 2;
int MARK = 3;
int SEARCH = 4;
int SERIAL = 5;
int CANCEL = 6;
int UP = 7;
int DOWN = 8;
int BAUD = 19200;

import processing.serial.*;
Serial myPort;
int port;
String portName;

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
                    new button("mark",300,24),
                    new button("search", 400, 24),
                    new button("serial", 500, 24),
                    new button("cancel", 600, 24),
                    new button("^", 682, 193, 18, 18),
                    new button("v", 682, 408, 18, 18)};
                    
ArrayList people;
String[] lines;

String date = "01/01/2012";
String prefix = "event_";
String namesFile = "";
String inString = null;
String inputText = "";
String fileName = "";

String message1 = "Open Serial port to begin scanning";
String message2 = "Open Names file to load tags";
String message3 = "Welcome to RPI ID Reader";
String message4 = "";

int currentEntry = 3;

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
  inString = inString.substring(0, 11);
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

void cancellAll(){
  buttons[SEARCH].clicked = false;
  buttons[LOAD].clicked = false;
  buttons[EDIT].clicked = false;
  buttons[ADD].clicked = false;
  buttons[SERIAL].clicked = false;
  buttons[CANCEL].clicked = false;
}

String makeString(person tperson){
  String tstring = "";
  tstring += tperson.name;
  tstring += ',';
  tstring += tperson.email;
  tstring += ',';
  tstring += tperson.role;
  return tstring;
}

void setup(){
  size(700, 450);
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
  rect(0, 166, 700, 3);
  rect(0, 190, 700, 3);
  rect(0, 426, 700, 3);
  
  //general text printing
  fill(textColor);
  textFont(font, 15);
  textAlign(CENTER);
  text("Press cancel at any time to return", 350, 445);
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
  
  if(buttons[EDIT].clicked && fileOpen){            //add new person
    if(message1.charAt(0) != 'S'){
      message("Scan ID, or enter \'First Last,email,role\'");
    }
    person tperson = (person) people.get(currentEntry);
    if(getText() != ""){
      String tstring[] = split(getText(), ',');
      tperson.name = tstring[0];
      tperson.email = tstring[1];
      tperson.role = tstring[2];
      inputText = "";
      inString = null;
      people.set(currentEntry,tperson);
      message("Entry updated successfully");
      buttons[EDIT].clicked = false;
    }
    if(inString != null){
      tperson.rfid = inString;
      inputText = "";
      inString = null;
      people.set(currentEntry,tperson);
      message("Entry updated successfully");
      buttons[EDIT].clicked = false;
    }
  }
  else buttons[EDIT].clicked = false;
  
  if(buttons[ADD].clicked && fileOpen){            //add new person
    if(message1.charAt(0) != 'E'){
      message("Enter \'First Last,email,role\' and scan ID");
    }
    if((getText() != "") && (inString != null)){
      String tstring[] = split(getText(), ',');
      people.add(new person(tstring[0], tstring[1], inString, tstring[2]));
      inputText = "";
      inString = null;
      buttons[ADD].clicked = false;
      message("New person added successfully");
      currentEntry = people.size();
    }
  }
  else buttons[ADD].clicked = false;
  
  if(buttons[MARK].clicked && fileOpen){
    person tperson = (person) people.get(currentEntry);
    if(!tperson.present)
      tperson.present = true;
    else
      tperson.present = false;
    buttons[MARK].clicked = false;
    mousePressed = false;
  }
  else buttons[MARK].clicked = false;
  
  if(buttons[SEARCH].clicked && fileOpen){
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
  else buttons[SEARCH].clicked = false;
  
  if(buttons[CANCEL].clicked){
    cancellAll();
    if(message1.charAt(0) != 'c')
      message("cancelling");
  }
  
  if(buttons[SERIAL].clicked){              //open/refresh serial port
    if(portOpen){                          //close open port
      myPort.stop();
      myPort.clear();
      portOpen = false;
    }
    if(message1.charAt(0) != 'P'){         //only do this once or the program will slow way down
      String tmessage = "Ports - ";
      for(int i=0; i<Serial.list().length; i++){
        tmessage += i;     //list each one with the corresponding user input to select
        tmessage += ": ";
        tmessage += Serial.list()[i];
        tmessage += ", ";
      }
      tmessage += "please select port";
      message(tmessage);
    }
      
    if(getText() != ""){
      port = getText().charAt(0)-48;
      portName = Serial.list()[port];
      myPort = new Serial(this, portName, BAUD);
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
  
  if(fileOpen){                       //print the list of people
    textAlign(RIGHT);
    text(fileName.substring(fileName.lastIndexOf('\\')+1), 695, 15);
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
      if(tperson.present)
        text("present", 560, 230+i*24);
    }
  }
  
  if(portOpen){
    textAlign(CENTER);                     //serial port name
    text(portName, 466, 15);
  }
  
  if(!fileOpen || !portOpen){              //port must be open and file loaded
    fill(#FF0000);
    textAlign(CENTER);
    text("NOT OK to scan", 233, 15);
  }
  
  else{                                    //if the port is open and the file is loaded
    fill(#00FF00);
    textAlign(CENTER);
    text("OK to scan", 233, 15);
    
    //always listening for an RFID on the serial port
    if((inString != null) && !buttons[ADD].clicked && !buttons[EDIT].clicked){//if there is an ID available
      //println(inString);
      if((currentEntry = search(inString)) < 0){
        message("rfid \"" + inString + "\" not found in file");
        buttons[ADD].clicked = true;
        currentEntry = 0;
      }
      else{
        message("rfid \"" + inString + "\" found at entry " + currentEntry);
        person tperson = (person) people.get(currentEntry);
        tperson.present = true;
        inString = null;
      }
    }
    //always doing other things
    
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
  String role;                          //officer, member, associate, advisor
  boolean present;                      //attendance
  
  person(String n){                  //create a person with a name only
    name = n;
    email = "";                          //blank RCSID
    rfid = "";                           //blank RFID
    role = "associate";                  //associate
    present = false;
  }
  
  person(String n, String e, String r){//create person with name, email, and rfid
    name = n;
    email = e;
    rfid = r;              
    role = "associate";               //change role as needed after addition
    present = false;
  }
  
  person(String n, String e, String r, String q){//create person with name, email, rfid, and role
    name = n;
    email = e;
    rfid = r;              
    role = q;
    present = false;
  }
}

private void prepareExitHandler(){
  Runtime.getRuntime().addShutdownHook(new Thread(new Runnable(){
    public void run(){
      System.out.println("SHUTDOWN HOOK");
      // application exit code here
      
      person tperson;
      String outData[];
      ArrayList present = new ArrayList();
      
      for(int i=0; i<people.size(); i++){
        tperson = (person) people.get(i);
        if(tperson.present){
          present.add(makeString(tperson));
        }
      }
      
      outData = new String[present.size()];
      outData = (String[]) present.toArray(outData);
      
      saveStrings((prefix + month() + day() + year() + ".txt"), outData);
      println("saved data");      
    }
  }));
}


