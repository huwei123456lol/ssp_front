from pyowm import OWM
owm = OWM('1939aa35b488ce5754b945be9bf4429f');
mgr = owm.weather_manager();
observation = mgr.weather_at_place('武汉,CN');
weather = observation.weather;
print(weather.temperature('celsius')); # 输出当前温度（摄氏度）
print(weather.wind()); # 输出当前风速（m/s）
print(weather.humidity()); # 输出当前湿度（%）
print(weather.pressure()); # 输出当前气压（hPa）