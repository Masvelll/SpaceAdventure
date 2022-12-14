# SpaceAdventure

Данный проект представляет собой игру на pygame.
Её цель - управлять космическим кораблём и разрушать метеориты, летящие навстречу.


Во время игры можно получать бонусы, способные либо временно увеличить мощность оружия, 
либо восполнить шкалу щита.


При достижении полосы щита нуля, игрок теряет одно здоровье,
а при достижении нуля полосы энергии уровень оружия понижается.


В игре имеется магазин, который позволяет улучшить стартовый уровень оружия, 
щит, а также скорость выстрела.


Помимо этого в игре есть опции, позволяющие регулировать уровень громкости,
как звуковых эффектов, так и самой музыки.


После достижения определённого числа очков начинают появляться враги, которые так же 
как и игрок способны стрелять.
Со временем уровень сложности увеличивается, то есть появляется всё больше и больше врагов.

### Установка

Необходимо склонировать репозиторий, а также скачать интерпретатор
Python, если у вас он отсутствует.

### Запуск

Запустите файл main.py

### Управление

Переключение между кнопками в меню осуществляется с помощью
стрелочек вниз, вверх на NumPad. В меню настроек уровни
громкости переключаются с помощью стрелочек вправо, влево.

Для управления игроком так же используются стрелки, для
выстрела можно нажимать кнопку space, либо удерживать её.

### Иходник

Проект написан на основе данного https://github.com/kidscancode/gamedev/blob/master/tutorials/shmup/shmup-14.py

Изначально уже была сделана основная архитектура кода
(около 370 строчек), однако большая часть проекта была
написана самостоятельно (около 2000 строчек). Причём
в исходнике было всё в одном файле, поэтому после
некоторых изменений в игре было достаточно тяжело распределить
всё по модулям, что было одной из основных задач данного проекта.