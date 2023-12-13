-- Create the stored procedure ComputeAverageWeightedScoreForUsers
DELIMITER //
CREATE PROCEDURE ComputeAverageWeightedScoreForUsers()
BEGIN
    DECLARE user_id_var INT;
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR SELECT id FROM users;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Open the cursor
    OPEN cur;

    -- Loop through each user
    read_loop: LOOP
        -- Fetch the user_id from the cursor
        FETCH cur INTO user_id_var;

        -- Break the loop if no more users
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Declare variables to store total weighted score and total weight
        DECLARE total_weighted_score FLOAT;
        DECLARE total_weight INT;

        -- Calculate the total weighted score and total weight for the current user
        SELECT SUM(corrections.score * projects.weight), SUM(projects.weight)
        INTO total_weighted_score, total_weight
        FROM corrections
        JOIN projects ON corrections.project_id = projects.id
        WHERE corrections.user_id = user_id_var;

        -- Calculate the average weighted score and update the users table
        IF total_weight > 0 THEN
            UPDATE users
            SET average_score = total_weighted_score / total_weight
            WHERE id = user_id_var;
        ELSE
            -- If there are no corrections, set average_score to 0
            UPDATE users
            SET average_score = 0
            WHERE id = user_id_var;
        END IF;
    END LOOP;

    -- Close the cursor
    CLOSE cur;
END //
DELIMITER ;
