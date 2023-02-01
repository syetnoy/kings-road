import sys

from PIL import Image
from pathlib import Path


def mirror(sp):
    for name in sp:
        image = Image.open(f'{name}')
        pixels = image.load()
        x, y = image.size
        for i in range(x // 2):
            for j in range(y):
                r, g, b, a = pixels[i, j]
                rr, gg, bb, aa = pixels[x - 1 - i, j]
                pixels[i, j] = rr, gg, bb, aa
                pixels[x - 1 - i, j] = r, g, b, a
        image.save(f'{name}')


def pixel(sp):
    for name in sp:
        image = Image.open(f'{name}')
        pixels = image.load()
        x, y = image.size
        if x == 516 and y == 420:
            z = 6
        else:
            continue
        if x == y == 900:
            z = 12
        if x == 720 and y == 480:
            z = 6
        R, G, B, A = 0, 0, 0, 0
        for i in range(0, x, z):
            for j in range(0, y, z):
                for ii in range(z):
                    for jj in range(z):
                        r, g, b, a = pixels[i + ii, j + jj]
                        R += r
                        G += g
                        B += b
                        A += a
                R //= z ** 2
                G //= z ** 2
                B //= z ** 2
                if R + G + B <= 30:
                    A = 0
                else:
                    A = 255
                for ii in range(z):
                    for jj in range(z):
                        pixels[i + ii, j + jj] = R, G, B, A
                R, G, B, A = 0, 0, 0, 0
        image.save(f'{name}')


def rename(sp):
    counter = 1
    for name in sp:
        image = Image.open(name)
        image.save(f"C:\\Users\\Владислав\\PycharmProjects\\King's Road\\Mobs\\{PERS}\\{Folder}\\satyr{counter}.png")
        counter += 1


def crop(sp):
    for name in sp:
        image = Image.open(name)
        print(name)
        x, y = image.size
        image = image.crop((0, 0, x, y - 10))
        image.save(name)


def set_size(sp):
    for name in sp:
        image = Image.open(name)
        print(name)
        x, y = image.size
        if x == 520 and y == 420:
            image = image.crop((0, 0, x - 4, y))
            image.save(name)


paths1 = ['FallenAngel1', 'FallenAngel2', 'FallenAngel3', 'Golem1', 'Golem2', 'Golem3',
          'Minotaur1', 'Minotaur2', 'Minotaur3', 'Reaper1', 'Reaper2', 'Reaper3',
          'Wraith1', 'Wraith2', 'Wraith3']

paths2 = ['Attaching', 'Dying', 'Staying', 'Walking', 'Angering', 'Hurting']
sv = ['Satyr1', 'Satyr2', 'Satyr3']
PERS, Folder = 'Satyr1', 'Angering'

sp = []
for i in sv:
    for j in paths2:
        folder = Path(f"C:\\Users\\Владислав\\PycharmProjects\\King's Road\\Mobs\\{i}\\{j}")

        for pic in folder.rglob('*'):
            sp.append(pic)
'''mirror(sp)
pixel(sp)
rename(sp)'''
set_size(sp)
pixel(sp)
