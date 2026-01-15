# TEE_BEE_DEE by JAMEs

## Roster/Roles:
Project Manager: Ethan Cheung  
Leaderboard Coder: Jason Chan  
Lyrics Coder: Matthew Ciu  
Database Coder: Amy Shrestha

**Description**: Our project is a website that creates the soon-to-be most popular song in the world. This is done by taking the most popular songs’ lyrics and randomly picking lines and putting them in an assigned template. Users can choose two songs from 6 randomly rolled top songs to create a mashup of both pieces using a pre-set algorithm. Top the leaderboard by creating the most songs!

## Install guide
1) Clone the repo into a local directory:
```
git clone git@github.com:echeung60/JAMEs.git
```
2) Enter the app directory:
```
cd JAMEs
```
3) Open a virtual environment:
```
python3 -m venv venv
```
4) Activate virtual env for Linux, Windows, or Mac:

i. Linux
```
. venv/bin/activate
```
ii. Windows
```
venv\Scripts\activate
```
iii. Mac
```
source venv/bin/activate
```
5) Install necessary modules:
```
pip install -r requirements.txt
```  
6) After running the launch codes and utilizing the app, exit the virtual environment:
```
deactivate
```

## Launch codes
1) Run the app through Flask:
```
python app/__init__.py
```
2) Open the website at website:
```
http://127.0.0.1:5000
```  
