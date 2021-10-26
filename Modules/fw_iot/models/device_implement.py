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
        "alert": {
            "fields": ["temperature"]
        },
        "data": {
            "action": "fw_iot.fwiot_device_thermometer_action",
            "schedule_id": "fw_iot.ir_cron_thermometer_get_data"
        },
        "setting": {
            "action": "fw_iot.fwiot_device_thermo_setting_wizard_action",
            "model": "fwiot_device_thermo_setting_wizard"
        }
    },
    {
        "code": ["SCANNER"],
        "model": "fwiot_device_scanner",
        "alert": {
            "fields": ["mac","ssid","tx_power","rssi"]
        },
        "data": {
            "action": "fw_iot.fwiot_device_scanner_action",
            "schedule_id": "fw_iot.ir_cron_scanner_get_data",
        },
        "setting": {
            "action": "fw_iot.fwiot_device_scanner_setting_wizard_action",
            "model": "fwiot_device_scanner_setting_wizard"
        }
    },
    {
        "code": ["SNIF"],
        "model": "fwiot_device_sniffer",
        "alert": {
            "fields": ["mac"]
        },
        "data": {
            "action": "fw_iot.fwiot_device_sniffer_action",
            "schedule_id": "fw_iot.ir_cron_sniffer_get_data",
        },
        "setting": {
            "action": "fw_iot.fwiot_device_sniffer_setting_wizard_action",
            "model": "fwiot_device_sniffer_setting_wizard"
        }
    },
    {
        "code": ["NFCREAD"],
        "model": "fwiot_device_nfc_reader",
        "alert": {
            "fields": ["rfid"]
        },
        "data": {
            "action": "fw_iot.fwiot_device_nfc_reader_action",
            "schedule_id": "fw_iot.ir_cron_nfc_reader_get_data",
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
            "schedule_id": "fw_iot.ir_cron_smoke_get_data",
        },
        "setting": {
            "action": "fw_iot.fwiot_device_smoke_detector_setting_wizard_action",
            "model": "fwiot_device_smoke_detector_setting_wizard"
        }
    }
]
