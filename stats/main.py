import json
import sympy as sym


# Check if a node at pos is leaf in binary heap array
def is_leaf(arr, pos, arr_len):
    return (2 * pos + 1 >= arr_len or arr[2 * pos + 1] is None) and (2 * pos + 2 >= arr_len or arr[2 * pos + 2] is None)


def get_prob_expr(test, fail):
    classifier = test[0].split(':')[0]
    match classifier:
        case 'r':
            specifier_str = test[0].split(':')[1]
            specifier = int(test[0].split(':')[1])
            x = sym.Symbol('r' + specifier_str)
            if specifier <= 5:
                expr = 1 - pow(sym.Rational(2, 3), x + test[1])
            else:
                expr = x
        case 'delayed':
            expr = sym.Symbol('delayed')
        case 'co':
            specifier = int(test[0].split(':')[1])
            match specifier:
                case 0:
                    expr = sym.Symbol('agreement')
                case 9:
                    expr = sym.Symbol('dark_pact')
                case _:
                    raise Exception('not implemented condition specifier {}'.format(specifier))
        case 'as':
            if len(test[0].split(':')) != 2:
                raise Exception('asset condition is implemented only with exactly one specifier')
            specifier = test[0].split(':')[1]
            match specifier:
                case 'item':
                    expr = sym.Symbol('as_item')
                case _:
                    raise Exception('asset condition unknown specifier {}'.format(specifier))
        case 'om':
            specifier = test[0].split(':')[1]
            match specifier:
                case 'blue':
                    expr = sym.Symbol('omen_blue')
                case 'red':
                    expr = sym.Symbol('omen_red')
                case 'green':
                    expr = sym.Symbol('omen_green')
                case _:
                    raise Exception('unknown omen specifier {}'.format(specifier))
        case _:
            raise Exception('unknown classifier {}'.format(classifier))
    if fail:
        expr = 1 - expr
    return expr


def get_stats():
    fi = open('rome.txt', 'r')
    encounters = []
    outcomes = {}
    for line in fi:
        line = [x.strip() for x in line.split('\t')]
        encounter = {
            'location': line[0],
            'id': int(line[1]),
            'set': line[2],
            'text': line[3],
            'actions': []
        }
        # Actions are tests and outcomes
        for node in line[4:]:
            if node == '':
                encounter['actions'].append(None)
            else:
                encounter['actions'].append(json.loads(node))

        encounters.append(encounter)
        actions = encounter['actions']
        ac_len = len(encounter['actions'])
        # print(len(line), encounter['actions'])

        for i, node in enumerate(actions):
            # Leafs are outcomes, tests have children
            if is_leaf(actions, i, ac_len):
                if i == 0:
                    raise Exception('Leaf at root position!')
                if node is None and ((i + 2 * (i % 2) - 1) >= ac_len or actions[i + 2 * (i % 2) - 1] is None):
                    # Node and its sibling are empty, their parent is responsible for registering no effect outcome
                    continue

                par_pos = (i - 1) // 2
                par = actions[par_pos]
                expr = get_prob_expr(par, i % 2 == 0)
                if par_pos > 0:
                    # node has grandparent
                    gpar_pos = (par_pos - 1) // 2
                    gpar = actions[gpar_pos]
                    expr *= get_prob_expr(gpar, par_pos % 2 == 0)

                if node is None:
                    key = 'no effect'
                    effects = []
                else:
                    key = json.dumps(sorted(node))
                    effects = node
                init_outcome = {'expr': 0, 'effects': []}
                outcomes[key] = {'expr': (outcomes.get(key, init_outcome)['expr'] + expr), 'effects': effects}

    total_sum = 0
    total_expr = 0
    res = []

    settings = {
        'r0': 4,
        'r1': 3,
        'r2': 2,
        'r3': 2,
        'r4': 2,
        'r5': 1,  # ok to spend resources r5-9
        'r6': 1,
        'r7': 1,
        'r8': 1,
        'r9': 1,
        'as_item': 1,  # usually acceptable
        'dark_pact': 0,  # hell no
        'delayed': 1,  # so so
        'agreement': 0,  # very bad
        'omen_blue': 1,  # pick your lucky omen!
        'omen_red': 0,
        'omen_green': 0
    }

    filter_effect = ["co:4", 1]  # blessing
    # filter_effect = ["r:4", 1]  # improve will
    # filter_effect = None

    print('Outcome filter {}:'.format(filter_effect))
    print('{0: <40} {1}'.format('outcomes', 'probability'))
    for key in outcomes.keys():
        if filter_effect is not None and filter_effect not in outcomes[key]['effects']:
            continue

        expr = outcomes[key]['expr'].evalf(subs=settings)
        total_sum += expr / len(encounters)
        total_expr += outcomes[key]['expr']
        res.append([key, expr / len(encounters)])

    res.sort(reverse=True, key=lambda x: x[1])
    for r in res:
        print('{0: <40} {1:.3%}'.format(r[0], 0 if r[1] < 1e-7 else r[1]))
    total_expr = sym.simplify(total_expr)
    variables = settings.keys()
    print('total probability {:.3%}, outcomes {}, total expr {}'.format(total_sum, len(res), total_expr))

    print('gradient')
    for variable in variables:
        new_settings = settings.copy()
        new_settings[variable] = settings[variable] + 1 if 'r0' <= variable <= 'r4' else min(1, settings[variable] + 1)
        diff =(total_expr.evalf(subs=new_settings) - total_expr.evalf(subs=settings)) / len(encounters)
        print('{0: <10} {1:.3%}'.format(variable, 0 if diff < 1e-7 else diff))


if __name__ == '__main__':
    get_stats()
