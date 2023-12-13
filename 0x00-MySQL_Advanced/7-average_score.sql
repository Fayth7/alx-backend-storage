-- Create a stored procedure ComputeAverageScoreForUser
DELIMITER //

CREATE PROCEDURE ComputeAverageScoreForUser(IN user_id_param INT)
BEGIN
    DECLARE total_score INT;
    DECLARE total_projects INT;
    DECLARE average_score FLOAT;

    -- Compute total score and total projects for the user
    SELECT SUM(score), COUNT(DISTINCT project_id)
    INTO total_score, total_projects
    FROM corrections
    WHERE user_id = user_id_param;

    -- Compute average score (if there are projects)
    IF total_projects > 0 THEN
        SET average_score = total_score / total_projects;
    ELSE
        SET average_score = 0;
    END IF;

    -- Update the user's average score
    UPDATE users
    SET average_score = average_score
    WHERE id = user_id_param;
END;
//

DELIMITER ;
