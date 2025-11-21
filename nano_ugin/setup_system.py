import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nano_ugin.settings')
django.setup()

from equipment.models import DeviceType, Parameter, DeviceModel, Device, ParameterValue
from django.contrib.auth.models import User, Group

def print_header(message):
    print(f"\n{'='*60}")
    print(f"🔄 {message}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def create_users_and_groups():
    print_header("СОЗДАНИЕ ПОЛЬЗОВАТЕЛЕЙ И ГРУПП")
    
    groups_data = ['Администраторы', 'Пользователи']
    
    groups = {}
    for name in groups_data:
        group, created = Group.objects.get_or_create(name=name)
        groups[name] = group
        if created:
            print_success(f"Создана группа: {name}")
        else:
            print_info(f"Группа уже существует: {name}")
    
    users_data = [
        {
            'username': 'admin',
            'password': 'admin',
            'email': 'admin@company.com',
            'first_name': 'Системный',
            'last_name': 'Администратор',
            'is_staff': True,
            'is_superuser': True,
            'groups': ['Администраторы']
        },
        {
            'username': 'user', 
            'password': 'user',
            'email': 'user@company.com',
            'first_name': 'Обычный',
            'last_name': 'Пользователь',
            'is_staff': False,
            'is_superuser': False,
            'groups': ['Пользователи']
        }
    ]
    
    for user_data in users_data:
        username = user_data.pop('username')
        password = user_data.pop('password')
        group_names = user_data.pop('groups')
        
        user, created = User.objects.get_or_create(
            username=username, 
            defaults=user_data
        )
        
        if created:
            user.set_password(password)
            user.save()
            for group_name in group_names:
                user.groups.add(groups[group_name])
            print_success(f"Создан пользователь: {username} (пароль: {password})")
        else:
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.set_password(password)
            user.save()
            user.groups.clear()
            for group_name in group_names:
                user.groups.add(groups[group_name])
            print_info(f"Обновлён пользователь: {username} (пароль: {password})")
    
    print_success("Все пользователи и группы созданы/обновлены!")

def create_device_types_and_parameters():
    print_header("СОЗДАНИЕ ТИПОВ УСТРОЙСТВ И ПАРАМЕТРОВ")
    
    device_types_data = [
        ("Коммутатор", "Сетевые коммутаторы и свитчи"),
        ("Камера", "Системы видеонаблюдения и камеры"),
        ("WiFi Точка доступа", "Беспроводные точки доступа"),
    ]
    
    device_types = {}
    for name, description in device_types_data:
        device_type, created = DeviceType.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        device_types[name] = device_type
        if created:
            print_success(f"Создан тип устройства: {name}")
        else:
            print_info(f"Тип устройства уже существует: {name}")
    
    parameters_data = [
        ("IP адрес", "ip_address", "text", True, "Основной IP адрес устройства", ["Коммутатор", "Камера", "WiFi Точка доступа"]),
        ("MAC адрес", "mac_address", "text", True, "Физический адрес устройства", ["Коммутатор", "Камера", "WiFi Точка доступа"]),
        ("Расположение", "location", "text", True, "Физическое расположение оборудования", ["Коммутатор", "Камера", "WiFi Точка доступа"]),
        ("Версия прошивки", "firmware_version", "text", False, "Версия firmware/ПО", ["Коммутатор", "Камера", "WiFi Точка доступа"]),
        ("Комментарий", "comment", "text", False, "Дополнительная информация", ["Коммутатор", "Камера", "WiFi Точка доступа"]),
        
        ("Количество портов", "port_count", "integer", True, "Общее количество портов", ["Коммутатор"]),
        ("Роль коммутатора", "switch_role", "text", False, "access/core/distribution", ["Коммутатор"]),
        
        ("Номер камеры", "camera_number", "integer", True, "Уникальный номер камеры", ["Камера"]),
        ("Наличие микрофона", "has_microphone", "boolean", False, "Встроенный микрофон", ["Камера"]),
        ("Угол обзора", "view_angle", "integer", False, "Угол обзора в градусах", ["Камера"]),
        
        ("SSID", "ssid", "text", True, "Идентификатор сети", ["WiFi Точка доступа"]),
        ("Азимут", "azimuth", "integer", False, "Направление антенны", ["WiFi Точка доступа"]),
        ("Высота антенны", "antenna_height", "float", False, "Высота в метрах", ["WiFi Точка доступа"]),
    ]
    
    for name, key, p_type, required, description, device_type_names in parameters_data:
        param, created = Parameter.objects.get_or_create(
            name=name, key=key,
            defaults={
                'parameter_type': p_type,
                'required': required,
                'description': description,
                'order': 0
            }
        )
        
        for type_name in device_type_names:
            param.device_types.add(device_types[type_name])
        
        if created:
            print_success(f"Создан параметр: {name} для {', '.join(device_type_names)}")
    
    print_success("Типы устройств и параметры созданы!")

def create_device_models():
    print_header("СОЗДАНИЕ МОДЕЛЕЙ УСТРОЙСТВ")
    
    device_types = {
        'Коммутатор': DeviceType.objects.get(name="Коммутатор"),
        'Камера': DeviceType.objects.get(name="Камера"),
        'WiFi Точка доступа': DeviceType.objects.get(name="WiFi Точка доступа"),
    }
    
    models_data = [
        ("BDCOM S2510-C", "Коммутатор", "24-портовый управляемый коммутатор"),
        ("TL-SG3428", "Коммутатор", "28-портовый гигабитный коммутатор"),
        ("DGS-3200-10", "Коммутатор", "10-портовый коммутатор уровня L2"),

        ("HiWatch DS-I114", "Камера", "Купольная IP-камера 4MP"),
        ("RVI-1NCT4030", "Камера", "Уличная IP-камера с ИК-подсветкой"),

        ("Ubiquiti UniFi", "WiFi Точка доступа", "Профессиональная точка доступа"),
        ("Tp-link EAP225", "WiFi Точка доступа", "Коммерческая точка доступа"),
    ]

    for name, type_name, description in models_data:
        model, created = DeviceModel.objects.get_or_create(
            name=name,
            device_type=device_types[type_name],
            defaults={'description': description}
        )
        if created:
            print_success(f"Создана модель: {name} ({type_name})")
    
    print_success("Модели устройств созданы!")

def create_test_devices():
    print_header("СОЗДАНИЕ ТЕСТОВЫХ УСТРОЙСТВ С ПАРАМЕТРАМИ")
    
    admin_user = User.objects.filter(is_superuser=True).first()
    
    test_devices_data = [
        {
            "name": "Коммутатор офис 101",
            "model": "BDCOM S2510-C", 
            "serial": "SW001",
            "status": "online",
            "parameters": {
                "ip_address": "192.168.1.10",
                "mac_address": "00:1B:44:11:3A:B7",
                "location": "Офис 101, 1 этаж",
                "firmware_version": "2.1.4",
                "port_count": 24,
                "switch_role": "access",
                "comment": "Основной коммутатор офиса"
            }
        },
        {
            "name": "Коммутатор серверная",
            "model": "TL-SG3428",
            "serial": "SW002", 
            "status": "offline",
            "parameters": {
                "ip_address": "192.168.1.11",
                "mac_address": "00:1B:44:11:3A:B8",
                "location": "Серверная комната",
                "firmware_version": "1.0.2",
                "port_count": 28,
                "switch_role": "core",
                "comment": "Коммутатор серверной стойки"
            }
        },
        {
            "name": "Коммутатор резерв",
            "model": "DGS-3200-10",
            "serial": "SW003",
            "status": "online",
            "parameters": {
                "ip_address": "192.168.1.12",
                "mac_address": "00:1B:44:11:3A:B9",
                "location": "Склад резерва",
                "firmware_version": "3.2.1",
                "port_count": 10,
                "switch_role": "access",
                "comment": "Резервный коммутатор"
            }
        },
        {
            "name": "Коммутатор этаж 2",
            "model": "Cisco Catalyst 2960",
            "serial": "SW004",
            "status": "online",
            "parameters": {
                "ip_address": "192.168.1.13",
                "mac_address": "00:1B:44:11:3A:C0",
                "location": "2 этаж, коридор",
                "firmware_version": "15.2.4",
                "port_count": 48,
                "switch_role": "distribution",
                "comment": "Коммутатор второго этажа"
            }
        },
        
        {
            "name": "Камера вход",
            "model": "HiWatch DS-I114",
            "serial": "CAM001",
            "status": "online", 
            "parameters": {
                "ip_address": "192.168.1.20",
                "mac_address": "00:1C:45:12:4B:C1",
                "location": "Главный вход",
                "firmware_version": "1.2.3",
                "camera_number": 1,
                "has_microphone": True,
                "view_angle": 90,
                "comment": "Камера наблюдения за входом"
            }
        },
        {
            "name": "Камера коридор",
            "model": "RVI-1NCT4030", 
            "serial": "CAM002",
            "status": "offline",
            "parameters": {
                "ip_address": "192.168.1.21",
                "mac_address": "00:1C:45:12:4B:C2",
                "location": "Центральный коридор",
                "firmware_version": "2.0.1",
                "camera_number": 2,
                "has_microphone": False,
                "view_angle": 120,
                "comment": "Камера наблюдения за коридором"
            }
        },
        {
            "name": "Камера кабинет",
            "model": "Secret Mini",
            "serial": "CAM003",
            "status": "online",
            "parameters": {
                "ip_address": "192.168.1.22",
                "mac_address": "00:1C:45:12:4B:C3",
                "location": "Кабинет директора",
                "firmware_version": "1.0.0",
                "camera_number": 3,
                "has_microphone": True,
                "view_angle": 180,
                "comment": "Камера кабинета руководства"
            }
        },
        {
            "name": "Камера парковка",
            "model": "Hikvision DS-2CD2143G0",
            "serial": "CAM004",
            "status": "online",
            "parameters": {
                "ip_address": "192.168.1.23",
                "mac_address": "00:1C:45:12:4B:C4",
                "location": "Парковка",
                "firmware_version": "5.6.1",
                "camera_number": 4,
                "has_microphone": False,
                "view_angle": 80,
                "comment": "Уличная камера парковки"
            }
        },
        
        {
            "name": "WiFi гостевой",
            "model": "Ubiquiti UniFi",
            "serial": "WIFI001",
            "status": "online",
            "parameters": {
                "ip_address": "192.168.1.30",
                "mac_address": "00:1D:46:13:5C:D1",
                "location": "Зона ресепшн",
                "firmware_version": "6.5.55",
                "ssid": "Guest-WiFi",
                "azimuth": 180,
                "antenna_height": 2.5,
                "comment": "Гостевая точка доступа"
            }
        },
        {
            "name": "WiFi офис", 
            "model": "Tp-link EAP225",
            "serial": "WIFI002",
            "status": "online",
            "parameters": {
                "ip_address": "192.168.1.31",
                "mac_address": "00:1D:46:13:5C:D2",
                "location": "Офисный блок",
                "firmware_version": "3.0.1",
                "ssid": "Office-WiFi",
                "azimuth": 90,
                "antenna_height": 3.0,
                "comment": "Корпоративная точка доступа"
            }
        },
        {
            "name": "WiFi склад",
            "model": "MikroTik cAP",
            "serial": "WIFI003",
            "status": "online",
            "parameters": {
                "ip_address": "192.168.1.32",
                "mac_address": "00:1D:46:13:5C:D3",
                "location": "Складское помещение",
                "firmware_version": "7.11.2",
                "ssid": "Warehouse-WiFi",
                "azimuth": 270,
                "antenna_height": 4.0,
                "comment": "Точка доступа склада"
            }
        },
    ]

    created_count = 0
    parameter_count = 0
    
    for device_data in test_devices_data:
        try:
            device_model = DeviceModel.objects.get(name=device_data["model"])
            
            device, created = Device.objects.update_or_create(
                serial_number=device_data["serial"],
                defaults={
                    'name': device_data["name"],
                    'device_model': device_model,
                    'status': device_data["status"],
                    'created_by': admin_user
                }
            )
            
            if created:
                created_count += 1
                print_success(f"Создано устройство: {device_data['name']} ({device_data['serial']})")
            else:
                print_info(f"Обновлено устройство: {device_data['name']} ({device_data['serial']})")
            
            print(f"🔧 Создаю параметры для: {device_data['name']}")
            device_param_count = create_device_parameters(device, device_data["parameters"])
            parameter_count += device_param_count
            print_success(f"   Добавлено параметров: {device_param_count}")
                
        except DeviceModel.DoesNotExist:
            print(f"❌ Модель не найдена: {device_data['model']}")
        except Exception as e:
            print(f"❌ Ошибка при создании устройства {device_data['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    print_success(f"Обработано устройств: {len(test_devices_data)}")
    print_success(f"Добавлено параметров: {parameter_count}")

def create_device_parameters(device, parameters_dict):
    param_count = 0
    
    for param_key, param_value in parameters_dict.items():
        try:
            parameter = Parameter.objects.get(key=param_key)
            
            param_value_obj, created = ParameterValue.objects.get_or_create(
                device=device,
                parameter=parameter
            )
            
            param_type = parameter.parameter_type

            param_value_obj.value_text = None
            param_value_obj.value_int = None
            param_value_obj.value_float = None
            param_value_obj.value_bool = None
            param_value_obj.value_date = None
            param_value_obj.value_datetime = None
            
            if param_value is not None:
                if param_type == 'text':
                    param_value_obj.value_text = str(param_value)
                elif param_type == 'integer':
                    param_value_obj.value_int = int(param_value)
                elif param_type == 'float':
                    param_value_obj.value_float = float(param_value)
                elif param_type == 'boolean':
                    param_value_obj.value_bool = bool(param_value)
                elif param_type == 'date':
                    param_value_obj.value_date = param_value
                elif param_type == 'datetime':
                    param_value_obj.value_datetime = param_value
            
            param_value_obj.save()
            param_count += 1
            
        except Parameter.DoesNotExist:
            print(f"❌ Параметр не найден: {param_key} для устройства {device.name}")
        except ValueError as e:
            print(f"❌ Ошибка преобразования значения {param_value} для параметра {param_key}: {e}")
        except Exception as e:
            print(f"❌ Общая ошибка для параметра {param_key}: {e}")
    
    return param_count

def setup_system():
    print_header("НАСТРОЙКА СИСТЕМЫ NANO-UGIN")
    
    try:
        create_users_and_groups()
        create_device_types_and_parameters()
        create_device_models()
        create_test_devices()

        print_header("ИТОГОВАЯ СТАТИСТИКА")
        print_success(f"👥 Пользователей: {User.objects.count()}")
        print_success(f"👥 Групп: {Group.objects.count()}")
        print_success(f"📊 Типов устройств: {DeviceType.objects.count()}")
        print_success(f"⚙️ Параметров: {Parameter.objects.count()}")
        print_success(f"📋 Моделей устройств: {DeviceModel.objects.count()}")
        print_success(f"🔧 Устройств: {Device.objects.count()}")
        print_success(f"📝 Значений параметров: {ParameterValue.objects.count()}")
        
        print_header("ДОСТУП К СИСТЕМЕ")
        print("👤 Доступные пользователи:")
        print("   admin / admin     - Полный доступ (администратор)")
        print("   user / user       - Обычный пользователь")
        
        print_header("🚀 СИСТЕМА ГОТОВА К РАБОТЕ!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при настройке системы: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    setup_system()