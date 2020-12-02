## Todo :

- [x] create worldweatheronline account
- [x] create function to get all data for one month
- [ ] create function that gets all data that we need (same as opendata Paris)
- [ ] convert hours to datetime and date to date
- [ ] convert other columns to innt or float

## Data available from the weather API :

### Daily data (one line per day)

- sun/moon rise and set hours, moon phase, moon illumination
- min, max & avg temperatures of the day (°C)
- UV index
- snowfall amount (cm)
- total sun hour (during the day?)

### Hourly data (24 lines per day)

- time (hour)
- real temperature & fells like temperature (°C)
- heat index (°C), dew point = température de rosée (°C)
- wind chill (°C), speed (m/s), gust = rafale (km/h), direction (°)
- weather code (synthetized data)
- precipitation (mm), humidity (%), visibility (km), pressure (mb), cloudcover (%), UV index

## Notes :

- min, max and avg daily temperature might be redondant with the hourly data
- same for UV index
