#!/usr/bin/env python

import json

from sqlalchemy import create_engine

SQL = '''
SELECT moves.identifier         AS name
     , moves.id                 AS number
     , types.identifier         AS type
     , damage.identifier        AS category
     , con_typ.identifier       AS contest
     , moves.pp                 AS pp
     , moves.power              AS power
     , moves.accuracy           AS accuracy
     , gen_names.name           AS generation
     , tm.item                  AS tm
     , hm.item                  AS hm
     , move_tutor.value         AS tutor
  FROM moves
  JOIN types
    ON types.id = moves.type_id
  JOIN move_damage_classes AS damage
    ON damage.id = moves.damage_class_id
  LEFT JOIN contest_types AS con_typ
    ON con_typ.id = moves.contest_type_id
  JOIN generation_names AS gen_names
    ON gen_names.generation_id = moves.generation_id
  LEFT JOIN (
        SELECT string_agg(distinct(items.identifier), ', ') AS item
             , moves.identifier AS move
          FROM machines
          JOIN items
            ON items.id = machines.item_id
          JOIN moves
            ON moves.id = machines.move_id
         WHERE items.identifier
          LIKE 'tm%%'
         GROUP BY moves.identifier
       ) AS tm
    ON moves.identifier = tm.move
  LEFT JOIN (
        SELECT string_agg(distinct(items.identifier), ', ') AS item
             , moves.identifier AS move
          FROM machines
          JOIN items
            ON items.id = machines.item_id
          JOIN moves
            ON moves.id = machines.move_id
         WHERE items.identifier
          LIKE 'hm%%'
         GROUP BY moves.identifier
       ) AS hm
    ON moves.identifier = hm.move
  LEFT JOIN (
        SELECT DISTINCT ON (move_id)
               move_id
             , true AS value
          FROM pokemon_moves
         WHERE pokemon_move_method_id = 3
         ORDER BY move_id
       ) AS move_tutor
    ON moves.id = move_tutor.move_id
 WHERE gen_names.local_language_id = 9
 ORDER BY number;
'''

def get_moves(engine):
    results = engine.execute(SQL)
    return [result for result in results]

def value_to_list(value):
    if value:
        return [str(e).strip() for e in value.split(',')]
    else:
        return []

def value_to_int(value):
    return int(value) if value else -1

def moves_to_dict(moves):
    return [{"name": str(move[0]),
             "number": value_to_int(move[1]),
	     "type": str(move[2]),
	     "category": str(move[3]),
	     "contest": str(move[4]),
	     "pp": value_to_int(move[5]),
	     "power": value_to_int(move[6]),
	     "accuracy": value_to_int(move[7]),
             "generation": str(move[8]),
	     "tm": value_to_list(move[9]),
	     "hm": value_to_list(move[10]),
             "tutor": True if move[11] else False} for move in moves]

def moves_to_json(pokemon):
    return json.dumps(moves_to_dict(pokemon))

if __name__ == '__main__':
    engine = create_engine('postgresql://@/pokedex')
    moves = get_moves(engine)
    print moves_to_json(moves)
