## Smart Home Office
### Aim
This project aims to create an application used for home environments, specifically targeting users who work remotely and have converted their rooms to Home Offices. It will use sensor devices to monitor environmental data and attempt to provide comfortable working conditions by controlling IoT devices such as smart plugs to power on electric heater, lights, etc.
### Equipment
Current equipment in use:
1. Oil-filled electric radiator
2. Tapo P100 Smart Plug
3. Raspberry Pi with SenseHat
### Services
Current services in use:
1. Blynk Web & Mobile App
2. IFTTT Web & Mobile App
3. ThingSpeak
4. Glitch
### Currently supported features
- Smart Plug control via Blynk
- Environmental data readings displayed on Blynk
- Mobile notifications for temperatue readings exceeding the target temperature via IFTTT app
- Set target temperature from Blynk using a slider widget
- Option to toggle notifications
- Safety feature: Turn off heating via Smart Plug if target temperature is exceeded
- Publish environmental data to ThingSpeak
- Check if user in at home by analysing WiFi network before turning off heater
- Environmental data charts from ThingSpeak embedded in Glitch web app with statistics
### Installation Guide
1. Install Tapo app from App Store / Play Store
2. Connect Tapo P100 Smart Plug to power
3. Pair the two devices and connect the Smart Plug to the WiFi
4. Create an account on IFTTT
5. Pair the Smart Plug with IFTTT service via Settings menu on mobile Tapo app
6. Create an account on Blynk
7. To create dashboard, use swith for: [Power, V0], [Notifications, V3], [Safety Control, V4], gauge for [Temperature, V1], and slider for: [Target Temperature, V2]
8. Create an account an ThingSpeak
9. Fill out the values in envTemplate.txt
10. Execute main.py file with the command given in the file (line 2)
### Future Planned features
- Store environmental data in Firebase
### Resources
- https://uk.mathworks.com/help/thingspeak/use-raspberry-pi-board-that-runs-python-websockets-to-publish-to-a-channel.html
- https://semantic-ui.com/

