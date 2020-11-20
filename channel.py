import random
import math

def exp_dist(alpha):
    return - math.log(random.random()) / alpha

def norm_dist():
    while True:
        Y = exp_dist(1)
        U = random.random()

        if U <= math.e**(-(Y - 1)**2/2):
            return Y

def norm_dist2(mu, sigma):
    return sigma * norm_dist() + mu

def module(function):
    def wrapper(*args, **kwargs):
        return abs(function(*args, **kwargs))
    return wrapper

@module
def next_ship(time, size):
    if size == 1:
        if 0 <= time <= 60 * 3:
            return norm_dist2(5, 2**0.5)
        if 60 * 3 <= time <= 60 * 9:
            return norm_dist2(15, 3**0.5)
        return norm_dist2(45, 3**0.5)

    if size == 2:
        if 0 <= time <= 60 * 3:
            return norm_dist2(3, 1)
        if 60 * 3 <= time <= 60 * 9:
            return norm_dist2(10, 5**0.5)
        return norm_dist2(35, 7**0.5)

    if size == 4:
        if 0 <= time <= 60 * 3:
            return norm_dist2(10, 2**0.5)
        if 60 * 3 <= time <= 60 * 9:
            return norm_dist2(20, 5**0.5)
        return norm_dist2(60, 9**0.5)

    print(time, size)
        
def ships_generator1():
    ships = [(next_ship(0, 2**i), 2**i) for i in range(3)]
    while True:
        ship = min(ships)
        if ship[0] > 60 * 12:
            break

        ships.remove(ship)
        ships.append((ship[0] + next_ship(*ship), ship[1]))

        yield ship

def ships_generator2():
    t = 0.0
    while True:
        size = 2**random.randint(0, 2)
        t += next_ship(t, size)
        if t > 60 * 12:
            break

        yield (t, size)

def ships_groups(ships_generator):
    ships = list(ships_generator())
    t = 0

    while ships:
        next_group = []
        ignored_ships = []

        rows = [0, 0]

        for ship in ships:
            if ship[1] + rows[0] <= 6:
                rows[0] += ship[1]
                next_group.append(ship)
            elif ship[1] + rows[1] <= 6:
                rows[1] += ship[1]
                next_group.append(ship)
            else:
                ignored_ships.append(ship)

        t = max(t, max(next_group)[0])
        yield (t, next_group)
        ships = ignored_ships

diquecycle = lambda group: exp_dist(4) + sum(exp_dist(2) for s in group) + \
                    exp_dist(7) + exp_dist(len(group) * 3/2)

infty = 2**64
def channel(diques, ships_generator):
    ship_groups_gen = ships_groups(ships_generator)

    t = Na = Nd = 0
    n = [[] for _ in range(diques)]
    TA, TD = [[] for _ in range(diques)], []
    try:
        a_group = next(ship_groups_gen)
        finished = False
    except StopIteration:
        finished = True
    Ti = [infty for _ in range(diques)]

    while True:
        tim = min(Ti)
        if not finished and a_group[0] <= tim:
            t = a_group[0]
            Na += 1
            n[0].append(a_group[1])      
            TA[0].append((t, a_group[1]))
            
            try:
                a_group = next(ship_groups_gen)
            except StopIteration:
                finished = True

            if len(n[0]) == 1:
                f_group = n[0][0]
                Ti[0] = t + diquecycle(f_group)
        else:
            for pos, ti in enumerate(Ti[:-1]):
                if ti == tim and len(n[pos]) > 0:
                    t = ti
                    f_group = n[pos].pop(0)
                    n[pos + 1].append(f_group)
                    TA[pos + 1].append((t, f_group))

                    Ti[pos] = infty if len(n[pos]) == 0 else (t + diquecycle(n[pos]))
                    
                    if len(n[pos + 1]) == 1:
                        f_group = n[pos + 1][0]
                        Ti[pos + 1] = t + diquecycle(f_group)

                    break
            else:
                if len(n[-1]) > 0:
                    t = Ti[-1]
                    Nd += 1
                    f_group = n[-1].pop(0)

                    Ti[-1] = infty if len(n[-1]) == 0 else (t + diquecycle(n[-1]))

                    TD.append((t, f_group))
                else:
                    return TA, TD

if __name__ == '__main__':
    iters = 1000

    for generator in [ships_generator1, ships_generator2]:
        by_size = []
        avg_w = []
        sum_w = []
        for _ in range(iters):
            TA, TD = channel(5, generator)

            acc = 0
            cnt = [0, 0, 0]
            for t, g in TD:
                for s in g:
                    acc += t - s[0]
                    cnt[s[1]//2] += 1

            by_size.append(cnt)
            avg_w.append(acc/sum(cnt))
            sum_w.append(acc)

        print(f'Cantidad de barcos promedio de cada tipo: {[sum(s[i] for s in by_size)/len(by_size) for i in range(3)]}')
        print(f'Cantidad de barcos promedio: {sum(sum(s) for s in by_size)/len(by_size)}')
        print(f'Cantidad de tiempo promedio que tarda en cruzar un barco: {sum(avg_w)/len(avg_w)}')
        print(f'Suma de tiempos de todas las esperas de los barcos promedio: {sum(sum_w)/len(sum_w)}')
        print('-'*80)
