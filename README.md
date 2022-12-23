## Smart Home Office
### Aim
This project aims to create an application used for home environments, specifically targeting users who work remotely and have converted their rooms to Home Offices. It will use sensor devices to monitor environmental data and attempt to provide comfortable working conditions by controlling IoT devices such as smart plugs to power on electric heater, lights, etc.
### Equipment
Current equipment in use:
1. Oil-filled electric radiator
2. Tapo P100 Smart Plug
3. Raspberry Pi with SenseHat
### Services
Current IoT services in use:
1. Blynk Web & Mobile App
2. IFTTT Web & Mobile App
### Currently supported features
- Smart Plug control via Blynk
- Environmental data readings displayed on Blynk
- Mobile notifications for temperatue readings exceeding the target temperature via IFTTT app
- Set target temperature from Blynk using a slider widget
- Option to toggle notifications
- Safety feature: Turn off heating via Smart Plug if target temperature is exceeded
### Planned features
- Environmental data sent to ThingSpeak
- Environmental data charts from ThingSpeak embedded in Glitch web app
- Check if user in at home by analysing WiFi network
### Known Issues
- When starting the app, the inital target temperature is 0 even though slider may be showing a different default value. 