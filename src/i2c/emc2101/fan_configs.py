#!/usr/bin/env python3
"""
"""

from enum import Enum


class RpmControlMode(Enum):
    VOLTAGE  = 1  # use supply voltage to control fan speed (2 and 3 pin fans)
    PWM      = 2  # use pulse width modulation to control fan speed (4 pin fans)


# basically a dataclass/attrs, but attrs are not available on CircuitPython
class FanConfig:

    def __init__(self, model: str, rpm_control_mode: RpmControlMode, minimum_duty_cycle: int, maximum_duty_cycle: int, minimum_rpm: int, maximum_rpm: int, pwm_frequency: int | None = None, steps: dict[int, tuple[int, int]] | None = None):
        self.model = model
        self.rpm_control_mode = rpm_control_mode
        if rpm_control_mode == RpmControlMode.PWM:
            if pwm_frequency is not None:
                self.pwm_frequency = pwm_frequency
            else:
                raise ValueError("must provide a PWM frequency for PWM fans")
        self.steps = steps
        if minimum_duty_cycle > maximum_duty_cycle:
            raise ValueError("minimum duty cycle must be smaller than maximum duty cycle")
        if minimum_duty_cycle >= 0:
            self.minimum_duty_cycle = minimum_duty_cycle
        else:
            raise ValueError("minimum duty cycle can't be negative")
        if maximum_duty_cycle <= 100:
            self.maximum_duty_cycle = maximum_duty_cycle
        else:
            raise ValueError("maximum duty cycle can't exceed 100%")
        self.minimum_rpm = minimum_rpm
        self.maximum_rpm = maximum_rpm


def export_fan_config(fan_config: FanConfig) -> dict[str, str | int]:
    if fan_config.rpm_control_mode == RpmControlMode.VOLTAGE:
        return {
            "model": fan_config.model,
            "control_mode": "VOLTAGE",
            "minimum_rpm": fan_config.minimum_rpm,
            "maximum_rpm": fan_config.maximum_rpm,
            "steps": fan_config.steps,
        }
    elif fan_config.rpm_control_mode == RpmControlMode.PWM:
        steps = {}
        for step, (dutycycle, rpm) in fan_config.steps.items():
            steps[step] = {
                "dutycycle": dutycycle,
                "rpm": rpm,
            }
        return {
            "model": fan_config.model,
            "control_mode": "PWM",
            "pwm_frequency": fan_config.pwm_frequency,
            "minimum_duty_cycle": fan_config.minimum_duty_cycle,
            "maximum_duty_cycle": fan_config.maximum_duty_cycle,
            "minimum_rpm": fan_config.minimum_rpm,
            "maximum_rpm": fan_config.maximum_rpm,
            "steps": steps,
        }
    else:
        raise ValueError("unknown control type")


def import_fan_config(fan_config: dict[str, str | int]) -> FanConfig:
    if fan_config["control_mode"] == "VOLTAGE":
        params = {
            "model": fan_config["model"],
            "control_mode": RpmControlMode.VOLTAGE,
            "minimum_rpm": fan_config["minimum_rpm"],
            "maximum_rpm": fan_config["maximum_rpm"],
            "steps": fan_config["steps"],
        }
        return FanConfig(**params)
    elif fan_config["control_mode"] == "PWM":
        params = {
            "model": fan_config["model"],
            "control_mode": RpmControlMode.PWM,
            "pwm_frequency": fan_config["pwm_frequency"],
            "minimum_duty_cycle": fan_config["minimum_duty_cycle"],
            "maximum_duty_cycle": fan_config["maximum_duty_cycle"],
            "minimum_rpm": fan_config["minimum_rpm"],
            "maximum_rpm": fan_config["maximum_rpm"],
            "steps": fan_config["steps"],
        }
        return FanConfig(**params)
    else:
        raise ValueError("unknown control type")


# provide reasonable default configurations for DC and PWM fans

# probably a bad idea to provide less than 50% supply voltage (fan might fail to start properly)
generic_dc_fan = FanConfig(model="generic DC fan", rpm_control_mode=RpmControlMode.VOLTAGE, minimum_duty_cycle=50, maximum_duty_cycle=100, minimum_rpm=100, maximum_rpm=2000)

# some fans treat a duty cycle of less than 20% as 'no signal' and go full speed instead
generic_pwm_fan = FanConfig(model="generic PWM fan", rpm_control_mode=RpmControlMode.PWM, minimum_duty_cycle=20, maximum_duty_cycle=100, minimum_rpm=100, maximum_rpm=2000, pwm_frequency=22500)
