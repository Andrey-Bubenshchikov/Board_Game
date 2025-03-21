# В этом файле описаны классы Unit и Squad и функция one_fight
# Моделирование боя проходит без учета перемещения (все бойцы могут "дотянутся" до всех бойцов)
# Моделирование боя проходит без учета очков действий

# Объявление экземпляров класса: 
# unit1 = Unit("Kostik"{имя}, 9{сила}, 7{ловкость}, 2{броня}, 2{атака})
# squad1 = Squad ("Bobiki"{имя}, [unit1,unit2,unit3]{список объектов класса Unit})

# one_fight:
# 1) выбираются цели .select_target_from_this_squad() - метод класса Squad
# 2) считается урон для каждого бойца (в отдельный атрибут юнита) .attack_on_this_unit() - метод класса Unit
# 3) урон засчитывается и все необходимые параметры сбрасываются .save_battle_result() - метод Squad
# 4) и так пока один из отрядов не погибнет целиком (погибшие юниты стираются из списка объекта Squad)
# 5) функция выводит текстовое значение: "win1" / "win2" / "draw_f" / "draw_t" (подробнее в самой функции)


import random

class Unit:
    name: str
    
    power: int
    agility: int
    armor: int
    attack: int

    # параметр для сохранение информации о сгенерированых значениях для проверки урона
    dice_values: list[int] = []

    # отложенный урон (нужен для удобства разбиения боя на этапы: выбор целей/определение урона/нанесение урона)
    damage_received:int = 0

    def __init__(self, name:str, power:int, agility:int, armor:int, attack:int):
        self.name = name # название бойца
        self.power = power # начальная сила
        self.agility = agility # ловкость(уворот)
        self.armor = armor # броня
        self.attack = attack # атака

        # параметр - список списков, для сохранения информации о силе и атаке нападающих юнитов [[сила1, атака1],[сила2, атака2]...]
        self.who_is_attack_me = [] 
    
    def __repr__(self):
        # Формируем строку для списка атакующих (сжатый формат)
        who_attack_str = ", ".join([f"[{attacker[0]}, {attacker[1]}]" for attacker in self.who_is_attack_me])

        # Формируем строку для значений кубиков (кодируем 10, 11, 12)
        dice_str = ", ".join(
            "A" if value == 10 else
            "B" if value == 11 else
            "C" if value == 12 else
            str(value)
            for value in self.dice_values
        )

        # Итоговая строка с требуемым форматом
        return (
            f"Имя: {self.name}\t\t|| "
            f"С:{self.power} Л:{self.agility} Б:{self.armor} А:{self.attack} ||\t"
            f"who_at({len(self.who_is_attack_me)}): {who_attack_str} \n"
            f"dice({len(self.dice_values)})-> Урон({self.damage_received})\t|| {dice_str} "
            
        )

    def attack_on_this_unit(self):
        
        # если бойца никто не атакует, выходим из функции
        if len(self.who_is_attack_me) == 0:
            return
        
        # блок подсчета количества кубиков для броска
        # переменная для подсчета количества кубаков для броска
        count_of_dice: int = 0
        
        # сумируем силу бойцов, которые атакуют 
        for i in self.who_is_attack_me:
            count_of_dice += i[0]
        
        # кол-во кубиков = сила атакующиъ бойцов / 2
        count_of_dice //= 2 

        # при атаке один на один к количеству кубиков добавляется атака напавшего бойца 
        if len(self.who_is_attack_me) == 1:
            count_of_dice += self.who_is_attack_me[0][1]

        #
        # генерируем значений броска кубиков
        self.dice_values = [random.randint(1, 12) for _ in range(count_of_dice)]
        # сортируем значения кубиков по возростанию для удобства чтения
        self.dice_values.sort()  

        # блок подсчета нанесенного урона
        # кубик со значением > ловкости атакованного наносят 1 урон, куб с значением = 12 наносит 2 урона
        for x in self.dice_values:
            if x > self.agility:
                self.damage_received+=1
            if x == 12:
                self.damage_received+=1
        
        # к урону добавляется показатель атаки всех атакующих бойцов
        for i in self.who_is_attack_me:
            self.damage_received += i[1]

        # из урона вычитается показатель брони атакованного
        self.damage_received -= self.armor
        if self.damage_received < 0:
            self.damage_received = 0 # чтобы избежать отрицательного урона

class Squad:
    name: str
    squad: list[Unit]
    dead: bool = False

    def __init__(self, name: str, squad: list [Unit]):
        self.name = name
        self.squad = squad
        
        # Создаем копию отряда для восстановления после проведенного боя
        self.save_squad = [Unit(unit.name, unit.power, unit.agility, unit.armor, unit.attack) 
                        for unit in squad]
    
    def __repr__(self):
        
        repr_from_units = ''
        for i in self.squad:
            repr_from_units += f'{repr(i)}'
            repr_from_units += f'\n------------------------------------------------------------------------------------\n'

        return(
            f'_________________________\n'
            f'{self.name} - Dead -> {self.dead}\n'
            f'_________________________\n'
            f'{repr_from_units}'
        )
    
    def select_target_from_this_squad(self, other):
        
        #если в одной из команд ноль бойцов, выходим из функции 
        if len(other.squad) == 0 or len(self.squad) == 0:
            return
        
        # Для каждого бойца текущего игрока выбирается случайный боец противника
        # Этому бойцу противника в переменную who_is_attack_me добавляется данные о силе и атаке 
        for i in self.squad:
            x = random.randint(0, len(other.squad) - 1) #случайное число - индекс атакованного юнита из other.squad
            other.squad[x].who_is_attack_me.append([i.power,i.attack]) # добавление параметров атакующего Unit'у из other.squad
    
    def save_battle_result(self):
        # для всех бойцов:
        # 1) из силы вычитается нанесенный урон
        # 2) нанесенный урон = 0 
        # 3) стирается информация об атакующих бойцах
        # 4) стирается информация о брошенных кубиках
        # 5) удаляет бойцов, если их сила стала <= 0
        # 6) проверяет гибель всех бойцов
        for i in self.squad:
            i.power -= i.damage_received
            i.damage_received = 0
            i.who_is_attack_me = []
            i.dice_values = []
            
        # создаем новый список для сохранению бойцов, чья сила > 0
        save_squad: list [Unit] = []
        for i in self.squad:
            if i.power > 0:
                save_squad.append(i)
        # обновляем список бойцов, исключив из него погибших бойцов (чья сила <= 0)
        self.squad = save_squad

        # если все бойцы погибли, сохраняем эту информацию в перемееной dead
        if len(self.squad) == 0:
            self.dead = True
    
    def rewrite(self):
        # функция для "воскрешения" отряда и обновления параметров силы бойцов на стартовые 
        
        # Флаг гибели отряда сбрасывается
        self.dead = False

        # Создаем копии бойцов из изначального состава отряда
        self.squad = [Unit(unit.name, unit.power, unit.agility, unit.armor, unit.attack) 
                    for unit in self.save_squad]

def one_fight(squad1: Squad, squad2: Squad) -> str:
    # симулирует один бой от начала до конца и выводит результат в виде слова/ключа:
    # "win1" - победил squad1 
    # "win2" - победил squad2
    # "draw_f" - ничья на основании уничтожения обоих банд
    # "draw_t" - ничья по истечению времени: банды не могут добить друг друга
    
    result_of_fight:str = ''
    t: int = 0 # переменная-счетчик для количества циклов

    while len(squad1.squad) != 0 and len(squad2.squad) != 0:
        
        # увеличиваем счетчик
        t+=1 

        # выбор целей для атаки
        squad2.select_target_from_this_squad(squad1)
        squad1.select_target_from_this_squad(squad2)
        
        # подсчет урона, нанесенного бойцам
        for i in squad1.squad:
            i.attack_on_this_unit()
        for i in squad2.squad:
            i.attack_on_this_unit()
        
        # Контроль/проверка/диагностика кода ///////////////////////////////////////////
        #print(f'////////////ВЫБОР ЦЕЛЕЙ и РАССЧЕТ УРОНА ({t} ход)/////////////')
        #print(repr(squad1))
        #print(repr(squad2))

        # подведение итогов атаки
        squad1.save_battle_result()
        squad2.save_battle_result()

        # Контроль/проверка/диагностика кода ///////////////////////////////////////////
        #print(f'////////////СОХРАНЕНИЕ УРОНА и ОБНОВЛЕНИЕ UNITOV ({t} ход)/////////////')
        #print(repr(squad1))
        #print(repr(squad2))

        if t > 30:
            break

    if squad1.dead and squad2.dead:
        result_of_fight = "draw_f"  # Оба отряда погибли
    elif squad1.dead:
        result_of_fight = "win2"  # Победил второй отряд
    elif squad2.dead:
        result_of_fight = "win1"  # Победил первый отряд
    else:
        result_of_fight = "draw_t"  # Ничья по времени (цикл завершился)
    
    # Контроль/проверка/диагностика кода ///////////////////////////////////////////
    #print(f'итог -> {result_of_fight} <- итог')
    return(result_of_fight)


#one_fight(squad1, squad2)
#squad1.rewrite()
#squad2.rewrite()

# Контроль/проверка/диагностика кода ///////////////////////////////////////////
#print(f'//////////// ПЕРЕЗАПИСЬ ОТРЯДОВ /////////////')
#print(repr(squad1))
#print(repr(squad2))


