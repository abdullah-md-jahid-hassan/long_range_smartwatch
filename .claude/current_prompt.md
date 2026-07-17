
Make The @documentation/plan/main_plan.md, @documentation/plan/iteration_1/step_1.md and like this[recursively].

As no smartwatch manufecturer not willing to give us the methods to impliment thous featcher we can get inspierd from android open source RAT tools. But we will use thouse featcher after user one time aknolagement(Will be implimented befor lunch - not now during development - may block featcher during dev) 


My plain plan
# List all feathers - What they do, how they work
All Feather Will be in 2 mode. Manual fetch(backend send request --> Mobile app weakup and send data to backend) and automatic at a interval[boolean flag determine this]

## Connection stablish
After Installing the app app will send connection request to the server(the server location will be pre seted but until deployment for development purpous editable from app) with proper connection detail(by which the server will send command/request to app. [you find out what is needed]). Then app will keep run in background but in shallow sleep only lissten to serve, do nothing. if command or request come. do it complitly and sallow sleep again. - Must be battry efficent

## Fetch All Basic info
1. Battery percentage
2. Lock or Unlocked - With For how long
3. Current Location
More Might be added letter. so need to make it modular

## Fetch Notifications
content: App name, Time, content ect.

## Fetch Massage
last N number of notification of [options]:
1. SMS
2. Whatsapp
3. Imo
4. Gmail
More Might be added letter. so need to make it modular

## Get N number of Call history with detail data

## Hear/save Audio 
1. Front Camera
2. Back camera

## Take Current Photo
1. Front Camera
2. Back camera

## Take video with audio live/save
1. Front Camera
2. Back camera

## Get Current Screenshot

## See live screen (No input)

## Remote Access with live view
- If locked - on click unlock

# Build the django server
build ui. 
build backend
build all api with documentation. Will not serve untill app core is ready. untill that place holder or dummy massge.

# Build the mobile app core wil all functionality. [No feather ui yet. only permission and connect ui]
Technologys
1. Java - Very common, Native Android SDK support, mature ecosystem
2. Kotlin - Increasingly common	Modern Android development language
we can go with any of them or combaine. Select the tecnology based on which is easy to build by ai agents. Complexity no problem as ai is going to help. but we need all featcher work smoothly

# connect server api and app api together

# Check if all core feather work

# Design The mobile UI

# Remove the admin ui in server

# Design watch interface

# connect watch with server






-- i have explained my current pain . some section are empty. you will complit thre full detail plan itaratively based on my given input and my intention. go through it itaratably for perfective the plan
