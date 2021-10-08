# -*- coding: utf-8 -*-
DEVICE_IMPLEMENT = [
    {
        "code": ["BEACON"],
        "model": "fwiot_device_beacon",
        "setting":{
            "action": "fw_iot.fwiot_device_beacon_setting_wizard_action",
            "model": "fwiot_device_beacon_setting_wizard"
        }
    },
    {
        "code": ["THERM1M"],
        "model": "fwiot_device_thermometer",
        "data": {
            "action": "fw_iot.fwiot_device_thermometer_action"
        },
        "action":{
            "action": "fw_iot.fwiot_device_thermo_action_wizard_action",
        },
        "setting": {
            "action": "fw_iot.fwiot_device_thermo_setting_wizard_action",
            "model": "fwiot_device_thermo_setting_wizard"
        }
    },
    {
        "code": ["SCANNER"],
        "model": "fwiot_device_scanner",
        "data": {
            "action": "fw_iot.fwiot_device_scanner_action",
        },
        "action":{
            "action": "fw_iot.fwiot_device_scanner_action_wizard_action",
        },
        "setting": {
            "action": "fw_iot.fwiot_device_scanner_setting_wizard_action",
            "model": "fwiot_device_scanner_setting_wizard"
        }
    },
    {
        "code": ["SNIF"],
        "model": "fwiot_device_sniffer",
        "data": {
            "action": "fw_iot.fwiot_device_sniffer_action",
        },
        "action":{
            "action": "fw_iot.fwiot_device_sniffer_action_wizard_action",
        },
        "setting": {
            "action": "fw_iot.fwiot_device_sniffer_setting_wizard_action",
            "model": "fwiot_device_sniffer_setting_wizard"
        }
    },
    {
        "code": ["NFCREAD"],
        "model": "fwiot_device_nfc_reader",
        "data": {
            "action": "fw_iot.fwiot_device_nfc_reader_action",
        },
        "action":{
            "action": "fw_iot.fwiot_device_nfc_reader_action_wizard_action",
        },
        "setting": {
            "action": "fw_iot.fwiot_device_nfc_reader_setting_wizard_action",
            "model": "fwiot_device_nfc_reader_setting_wizard"
        }
    },
    {
        "code": ["SMOKE"],
        "model": "fwiot_device_smoke_detector",
        "data": {
            "action": "fw_iot.fwiot_device_smoke_detector_action",
        },
        "action":{
            "action": "fw_iot.fwiot_device_smoke_detector_action_wizard_action",
        },
        "setting": {
            "action": "fw_iot.fwiot_device_smoke_detector_setting_wizard_action",
            "model": "fwiot_device_smoke_detector_setting_wizard"
        }
    }
]
