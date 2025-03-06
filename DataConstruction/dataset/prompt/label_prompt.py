def get_image_english_label_prompt():
   prompt="""
You are an expert in classification systems. Please classify the given image according to the following classification system:

### Weather Conditions
- **Clear**
- **Cloudy**
- **Overcast or Night**
- **Light Rain**
- **Moderate or Heavy Rain**
- **Snowy**
- **Foggy**
- **Dust/Sandstorm Weather**
- **Unknown:** e.g., indoor, inside tunnels

### Roadway
1. **Urban Roads**
   - **Residential Area Roads:** Low-speed limits, narrow, with many parked cars and frequent pedestrian activity. Example: roads within a community or residential alleys.
   - **Commercial Area Roads:** Near shops or malls, often with cargo trucks loading and unloading, and many pedestrians. Example: roads around shopping centers.
   - **Ring Roads/Express Loops:** Similar to elevated roads, connecting the main transportation systems of a city, with higher speeds but heavy traffic. Example: city outer ring roads (e.g., Beijing Fourth Ring Road).
   - **Urban Arterial Roads:** Non-residential, non-commercial, or ring/express loop roads, serving functional places nearby (e.g., parks, office zones, schools). Example: urban park loops, main roads around hospitals.

2. **Rural Roads**
   - **Small Village Roads:** Narrow, without lane markings, poor condition (muddy or gravel). Example: small roads between villages.
   - **Rural Multi-lane Roads:** Clearly marked with lanes, few vehicles, higher speeds. Example: major roads between towns.
   - **Farm Roads:** Dirt or grass roads, uneven surfaces, mainly for agricultural machinery. Example: roads around rural farmland.
   - **Forest or Hill Roads:** Natural terrain crossings with small slopes, sharp turns, and gravel surfaces.

3. **Highways**
   - **National/Provincial Roads:** Main roads between cities with clear traffic signs, sometimes passing through towns. Example: G105 National Road.
   - **Intercity Highways:** For long-distance travel, no at-grade intersections, smooth traffic flow. Example: G1 Beijing-Shanghai Expressway.
   - **Urban Highways:** Dense entry and exit ramps, heavy traffic, combines city commuting scenarios.

4. **Special Roads**
   - **Mountain Roads:** Winding, steep slopes, and sharp turns, some sections with limited visibility. Example: Sichuan-Tibet Line, Wuling Mountain Roads.
   - **Coastal Roads:** Built along the coastline, may be affected by wind speed or tides. Example: Hainan's East Line Expressway.
   - **Desert Roads:** Mostly soft sand, possibly unpaved, needing adaptation to desert conditions. Example: Tarim Desert Highway.
   - **Forest Roads:** Near woods, possible muddy patches, fallen branches, etc.
   - **High Mountain Ice and Snow Roads:** Slippery and cold in winter, possibly requiring anti-skid equipment.

5. **Parking Lots and Private Roads**
   - **Parking Lots:** Dense parking spaces, many blind spots for pedestrians.
   - **Private/Exclusive Roads:** Roads for specific units, park roads, construction roads, with limited vehicle types.

6. **Special/Other Types of Roads**
   - **Construction Zones:** Temporary traffic signs, complex road conditions, strict speed limits.
   - **Tunnels:** Poor ventilation and lighting, height and speed restrictions.
   - **Bridges:** May have steep slopes, need to prevent vehicles from losing control in strong winds.
   - **Flooded Roads/Waterlogged Sections:** Water accumulation after heavy rain, easy to skid or stall.
   - **Other Roads**

### Driving Status
- **Moving:** The vehicle is in motion
- **Stopped:** The vehicle is at rest

### Shooting Angle
- **Inside the Vehicle:** The image content is inside the vehicle
- **Outside the Vehicle**
  - **Front:** The image content is the front view of the vehicle
  - **Side:** The image content is the side view of the vehicle
  - **Rear:** The image content is the rear view of the vehicle

Please classify the following image according to this classification system.

#### **Output Format**
Please output the classification results in the following format, with each image corresponding to one line:
```
[{"Road Condition Primary Label":"Primary Road Label","Road Condition Secondary Label":"Secondary Road Label","Weather Condition":"Weather Condition","Driving Status":"Moving or Stopped","Shooting Angle":"Shooting Angle Classification"}]
```

> **Note: Only output content in the above format, do not generate any extra words, explanations, or descriptions!!!**
"""
   return prompt