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
          LIKE 'tm%'
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
          LIKE 'hm%'
         GROUP BY moves.identifier
       ) AS hm
    ON moves.identifier = hm.move
 WHERE gen_names.local_language_id = 9
 ORDER BY number;
