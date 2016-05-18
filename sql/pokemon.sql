SELECT poke.identifier  AS name
     , poke.species_id  AS number
     , gen_names.name   AS generation
     , typ.types        AS types
     , spec_names.genus AS genus
     , poke.height
     , poke.weight
     , poke.base_experience
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
        SELECT genus
             , pokemon_species_id
             , name
          FROM pokemon_species_names
         WHERE local_language_id = 9
       ) AS spec_names
    ON spec_names.pokemon_species_id = poke.species_id
 WHERE poke.is_default = 't'
   AND gen_names.local_language_id = 9
 ORDER BY poke.species_id;


SELECT poke.identifier AS name
     , typ.identifier  AS types
  FROM pokemon_types   AS poke_types
  JOIN pokemon AS poke
    ON poke_types.pokemon_id = poke.id
  JOIN types AS typ
    ON poke_types.type_id = typ.id;
