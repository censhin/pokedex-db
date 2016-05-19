#!/usr/bin/env python

import json

from sqlalchemy import create_engine

SQL = '''
SELECT poke.identifier            AS name
     , poke.species_id            AS number
     , gen_names.name             AS generation
     , typ.types                  AS types
     , base_stats.stats           AS base_stats
     , spec_names.genus           AS genus
     , poke.height                AS height
     , poke.weight                AS weight
     , species.capture_rate       AS capture_rate
     , poke.base_experience       AS base_experience
     , poke_abilities.identifier  AS abilities
     , ev.ev_data                 AS effort_values
     , poke_egg_groups.identifier AS egg_groups
     , evolution.evol_data        AS evolution
  FROM pokemon AS poke
  JOIN pokemon_species AS species
    ON poke.identifier = species.identifier
  JOIN generation_names AS gen_names
    ON species.generation_id = gen_names.generation_id
  JOIN (
	SELECT poke.identifier AS name
	     , string_agg(typ.identifier, ', ')  AS types
	  FROM pokemon_types   AS poke_types
	  JOIN pokemon AS poke
	    ON poke_types.pokemon_id = poke.id
	  JOIN types AS typ 
	    ON poke_types.type_id = typ.id
         GROUP BY poke.identifier
       ) AS typ
    ON typ.name = poke.identifier
  JOIN (
        SELECT poke_stats.pokemon_id
             , string_agg(concat(stats.identifier, ': ', poke_stats.base_stat), ', ') AS stats
          FROM pokemon_stats AS poke_stats
          JOIN stats
            ON stats.id = poke_stats.stat_id
         GROUP BY poke_stats.pokemon_id
       ) AS base_stats
    ON poke.species_id = base_stats.pokemon_id
  JOIN (
        SELECT genus
             , pokemon_species_id
             , name
          FROM pokemon_species_names
         WHERE local_language_id = 9
       ) AS spec_names
    ON spec_names.pokemon_species_id = poke.species_id
  JOIN (
        SELECT string_agg(abil.identifier, ', ') AS identifier
             , poke_abil.pokemon_id
          FROM pokemon_abilities as poke_abil
          JOIN abilities as abil
            ON poke_abil.ability_id = abil.id
         GROUP BY poke_abil.pokemon_id
       ) AS poke_abilities
    ON poke_abilities.pokemon_id = poke.species_id
  JOIN (
        SELECT poke_stats.pokemon_id
             , string_agg(concat(stats.identifier, ': ', poke_stats.effort), ', ') AS ev_data
          FROM pokemon_stats AS poke_stats
          JOIN stats
            ON stats.id = poke_stats.stat_id
         WHERE poke_stats.effort > 0
         GROUP BY poke_stats.pokemon_id
       ) AS ev
    ON ev.pokemon_id = poke.species_id
  JOIN (
        SELECT pokemon.identifier AS poke_identifier
             , pokemon.species_id AS species_id
             , string_agg(egg_groups.identifier, ', ') AS identifier
          FROM pokemon_egg_groups AS poke_egg
          JOIN egg_groups
            ON poke_egg.egg_group_id = egg_groups.id
          JOIN pokemon
            ON pokemon.species_id = poke_egg.species_id
         WHERE pokemon.is_default = 't'
         GROUP BY pokemon.identifier, pokemon.species_id
       ) AS poke_egg_groups
    ON poke_egg_groups.species_id = poke.species_id
  LEFT JOIN (
        SELECT poke_evol.id
             , poke_evol.evolved_species_id
             , concat(poke.identifier, ', ', poke_evol.evolved_species_id, ', ', poke_evol.minimum_level) AS evol_data
          FROM pokemon_evolution AS poke_evol
          JOIN pokemon AS poke
            ON poke.species_id = poke_evol.evolved_species_id
         WHERE poke.is_default = 't'
       ) AS evolution
    ON poke.species_id = evolution.id
 WHERE poke.is_default = 't'
   AND gen_names.local_language_id = 9
 ORDER BY poke.species_id;
'''

def get_pokemon(engine):
    result = engine.execute(SQL)
    return [poke for poke in result]

def value_to_list(value):
    return [str(e).strip() for e in value.split(',')]

def stats_to_dict(stats):
    d = {}
    stats_list = [stat.split(':') for stat in stats.split(',')]
    for s in stats_list:
        d[str(s[0]).strip()] = int(s[1])
    return d

def evolution_to_dict(evolution):
    if evolution:
        evo = [e.strip() for e in str(evolution).split(',')]
        return {
            "name": evo[0],
            "number": evo[1],
            "level": evo[2]
        }
    else:
        return None

def pokemon_to_dict(pokemon):
    return [{"name": str(poke[0]),
             "number": int(poke[1]),
             "generation": str(poke[2]),
             "types": value_to_list(poke[3]),
             "baseStats": stats_to_dict(poke[4]),
             "genus": str(poke[5]),
             "height": int(poke[6]),
             "weight": int(poke[7]),
             "captureRate": int(poke[8]),
             "baseExperience": int(poke[9]),
             "abilities": value_to_list(poke[10]),
             "effortValues": stats_to_dict(poke[11]),
             "eggGroups": value_to_list(poke[12]),
             "evolution": evolution_to_dict(poke[13])} for poke in pokemon]

def pokemon_to_json(pokemon):
    return json.dumps(pokemon_to_dict(pokemon))

if __name__ == '__main__':
    engine = create_engine('postgresql://@/pokedex')
    pokemon = get_pokemon(engine)
    print pokemon_to_json(pokemon)
