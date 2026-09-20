"""
[pin.label]
en = "Pins"
zh-hans = "引脚"
"""

from machine import ADC, PWM, Pin

try:
    from machine import DAC
except ImportError:
    DAC = None


__all__ = (
    "set_level",
    "set_dac",
    "set_pwm",
    "set_pwm_freq",
    "set_pwm_pulse",
    "get_adc",
    "is_high",
    "is_low",
)


used_pins = {}


def __get_pin(pin_num, pin_type):
    if isinstance(pin_num, Pin):
        pin = pin_num
    elif isinstance(pin_num, (ADC, PWM)) or (DAC and isinstance(pin_num, DAC)):
        return pin_num
    elif type(pin_num) is int:
        pin = used_pins.get(pin_num, None)
        if pin is not None:
            return pin
        pin = Pin(pin_num)
    else:
        raise TypeError("pin must be int or Pin")

    if type(pin_type) is ADC:
        pin = ADC(pin)
    elif type(pin_type) is PWM:
        pin = PWM(pin, freq=5000)
    elif DAC and type(pin_type) is DAC:
        pin = DAC(pin)
    return used_pins.setdefault(pin_num, pin)


def set_level(pin=1, val=1) -> None:
    """
    protected = true

    [label]
    en = "set pin (pin) level to (val)"
    zh-hans = "将引脚 (pin) 设为 (val) 电平"

    [[menu.pin]]
    data = "GPIO"

    [[menu.level]]
    value = 1
    [menu.level.label]
    en = "high"
    zh-hans = "高"

    [[menu.level]]
    value = 0
    [menu.level.label]
    en = "low"
    zh-hans = "低"
    """
    dpin = __get_pin(pin, Pin)
    dpin.init(Pin.OUT)
    dpin.value(val)


def set_dac(pin=1, val: int = 128) -> None:
    """
    protected = true

    [label]
    en = "set analog pin (pin) to (val|0-255)"
    zh-hans = "将模拟引脚 (pin) 设为 (val|0-255)"

    [[menu.pin]]
    data = "GPIO"
    """
    dac = __get_pin(pin, DAC)
    dac.write(min(max(val, 0), 255))


def set_pwm(pin=1, duty: int = 500) -> None:
    """
    protected = true

    [label]
    en = "set pwm pin (pin) duty to (duty|0-65535)"
    zh-hans = "将 PWM 引脚 (pin) 占空比设为 (duty|0-65535)"

    [[menu.pin]]
    data = "GPIO"
    """
    pwm = __get_pin(pin, PWM)
    pwm.duty_u16(duty)


def set_pwm_freq(pin=1, freq: int = 5000) -> None:
    """
    protected = true

    [label]
    en = "set pwm pin (pin) freq to (freq|0+)"
    zh-hans = "将 PWM 引脚 (pin) 频率设为 (freq|0+)"

    [[menu.pin]]
    data = "GPIO"
    """
    pwm = __get_pin(pin, PWM)
    pwm.freq(freq)


def set_pwm_pulse(pin=1, ns: int = 1000) -> None:
    """
    protected = true

    [label]
    en = "set pwm pin (pin) pulse width to (ns|0+) ns"
    zh-hans = "将 PWM 引脚 (pin) 脉冲宽度设为 (ns|0+) ns"

    [[menu.pin]]
    data = "GPIO"
    """
    pwm = __get_pin(pin, PWM)
    pwm.duty_ns(ns)


def get_adc(pin=1) -> int:
    """
    protected = true

    [label]
    en = "analog pin (pin) value"
    zh-hans = "模拟引脚 (pin) 值"

    [[menu.pin]]
    data = "GPIO"
    """
    adc = __get_pin(pin, ADC)
    return adc.read_u16()


def is_high(pin=1, pull=None) -> bool:
    """
    protected = true

    [label]
    en = "pin (pin) -> with (pull) <- is high level?"
    zh-hans = "引脚 (pin) -> (pull) <- 是高电平?"

    [[menu.pin]]
    data = "GPIO"

    [[menu.pull]]
    value = "None"
    [menu.pull.label]
    en = "none"
    zh-hans = "无"

    [[menu.pull]]
    value = "Pin.PULL_UP"
    [menu.pull.label]
    en = "pull up"
    zh-hans = "上拉"

    [[menu.pull]]
    value = "Pin.PULL_DOWN"
    [menu.pull.label]
    en = "pull down"
    zh-hans = "下拉"
    """
    dpin = __get_pin(pin, Pin)
    dpin.init(Pin.IN, pull)
    return bool(dpin.value())


# expands


def irq(pin=1) -> None:
    """
    protected = true

    [label]
    """
    pass


def irq_on(pin=1) -> None:
    pass


def irq_off(pin=1) -> None:
    """
    protected = true

    [label]
    """
    pass
