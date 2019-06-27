# Section concept

Section is a group of products with flat structure.
Products are grouped to sections by *product type* principle.
Technically it looks just like category, but has no hierarchy.
And it looks like [series](https://github.com/fidals/stroyprombeton/blob/master/doc/series.md),
but section is related to the a product instead of option.

## Examples
There is the full list of sections for the moment:
```
Блоки железобетонные
Плиты железобетонные
Лотки железобетонные
Колонны железобетонные
Ригели железобетонные
Панели железобетонные
Балки железобетонные
Стойки железобетонные
Фундаменты железобетонные
Ступени железобетонные
Трубы железобетонные
Сваи железобетонные
Короба железобетонные
Опоры железобетонные
```

## Problem
Our main categories data hierarchy has been built according to *construction types* principle.
There are base construction types:
```
Дорожное строительство
Строительство энергетических объектов
Общегражданское и промышленное строительство
Строительство инженерных сетей
```

Some time later we became needed for the new data hierarchy based on *product type*.
It's not hierarchy, but flat structure, as you see.


## Solution

We could not merge *product types* to the *construction types*
because of hierarchy conflicts.
For example both `Дорожное строительство` and `Общегражданское и промышленное строительство`
construction types have the same category `Сваи` with different products inside.

That's why we introduced Section concept.
It's yet another structure over the products with it's own navigation and features.
