-- List bands with Glam rock as their main style, ranked by longevity
SELECT band_name,
       IF(splitted[2] != '0000', formed, IF(splitted[1] != '0000', splitted[1], 2022)) as lifespan
FROM (
    SELECT band_name,
           SPLIT_STR(formed, '-', 3) as formed,
           SPLIT_STR(split, '-', 3) as split
    FROM bands
    WHERE style = 'Glam rock'
) AS glam_bands
ORDER BY lifespan DESC;
