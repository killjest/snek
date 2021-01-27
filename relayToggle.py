from gpiozero import LED
from time import sleep

light = LED(26)
heat = LED(20)
pump = LED(21)

while True:
    light.on()
    heat.off()
    pump.off()
    sleep(1)
    light.off()
    heat.on()
    pump.off()
    sleep(1)
    light.off()
    heat.off()
    pump.on()
    sleep(1)