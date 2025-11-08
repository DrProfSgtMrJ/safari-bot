
UPDATE safari_inventory
SET pokeballs = CASE
  WHEN user_id = 11 THEN pokeballs - 3
  WHEN user_id = 21 THEN pokeballs + 3
  ELSE bait
END
WHERE user_id IN (11, 21)
