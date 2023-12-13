-- Rank country origins of bands by the number of (non-unique) fans
SELECT origin, SUM(nb_fans) as nb_fans
FROM bands
GROUP BY origin
ORDER BY nb_fans DESC;
