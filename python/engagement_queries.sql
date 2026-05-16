-- ============================================================
-- Engagement metrics for RekenRangers
-- Generated from 1 CSV file(s):
--   - group_Conditie_4.csv
-- ============================================================

-- ============================================================
-- CONDITION: Conditie_4    (n = 26)
-- ============================================================

-- ------------------------------------------------------------
-- [Conditie_4] 1) UNUSED COINS / SPENDING RATIO (puzzle engagement)
-- ------------------------------------------------------------
SELECT
    'Conditie_4'                                             AS condition_label,
    s.username,
    COALESCE(sp.points, 0)                                AS unused_coins,
    COALESCE(SUM(p.piece_cost), 0)                        AS spent_coins,
    COALESCE(sp.points, 0) + COALESCE(SUM(p.piece_cost), 0) AS total_earned,
    ROUND(
        COALESCE(SUM(p.piece_cost), 0)
        / NULLIF(COALESCE(sp.points,0) + COALESCE(SUM(p.piece_cost),0), 0) * 100,
        1
    ) AS pct_spent,
    COUNT(spp.id)                                         AS pieces_unlocked
FROM students s
LEFT JOIN student_points sp         ON sp.student_id = s.id
LEFT JOIN student_puzzle_pieces spp ON spp.student_id = s.id
LEFT JOIN puzzles p                 ON p.id = spp.puzzle_id
WHERE s.username IN (
        'Ahmed Bouyahyaoui',
        'Alia Mansouri',
        'Amélie Sobrie',
        'Arthur Vanhauwaert',
        'Bilal Tayarsift',
        'Carlo Vetro',
        'Dario Casado',
        'Duke Wandje',
        'Eveleen Kaur',
        'Faith Geurts Mertens',
        'Firass BenameurMoumen',
        'Guillaume Ghistelinck',
        'Ina Gielen',
        'Juna Stoffels',
        'Kelly Martins Barroso',
        'Lee Goossens',
        'Lennert Machiels',
        'Lianne Noelmans',
        'Lucas Somers',
        'Léonié Fieuw',
        'Maya Milissen',
        'Mona El Mannouchi',
        'Remco Dick',
        'Sarah Ouali',
        'Siebe Corstjens',
        'Tijl Van Suetendael'
)
GROUP BY s.id, s.username, sp.points
ORDER BY pct_spent ASC;


-- ------------------------------------------------------------
-- [Conditie_4] 2) PUZZLES COMPLETED PER STUDENT
-- ------------------------------------------------------------
SELECT
    'Conditie_4'                                             AS condition_label,
    s.username,
    SUM(CASE WHEN owned_pieces = p.rows_count * p.cols_count THEN 1 ELSE 0 END) AS puzzles_completed,
    SUM(CASE WHEN owned_pieces > 0 AND owned_pieces < p.rows_count * p.cols_count THEN 1 ELSE 0 END) AS puzzles_started,
    COUNT(DISTINCT p.id) AS puzzles_touched
FROM students s
JOIN (
    SELECT student_id, puzzle_id, COUNT(*) AS owned_pieces
    FROM student_puzzle_pieces
    GROUP BY student_id, puzzle_id
) spp ON spp.student_id = s.id
JOIN puzzles p ON p.id = spp.puzzle_id
WHERE s.username IN (
        'Ahmed Bouyahyaoui',
        'Alia Mansouri',
        'Amélie Sobrie',
        'Arthur Vanhauwaert',
        'Bilal Tayarsift',
        'Carlo Vetro',
        'Dario Casado',
        'Duke Wandje',
        'Eveleen Kaur',
        'Faith Geurts Mertens',
        'Firass BenameurMoumen',
        'Guillaume Ghistelinck',
        'Ina Gielen',
        'Juna Stoffels',
        'Kelly Martins Barroso',
        'Lee Goossens',
        'Lennert Machiels',
        'Lianne Noelmans',
        'Lucas Somers',
        'Léonié Fieuw',
        'Maya Milissen',
        'Mona El Mannouchi',
        'Remco Dick',
        'Sarah Ouali',
        'Siebe Corstjens',
        'Tijl Van Suetendael'
)
GROUP BY s.id, s.username
ORDER BY puzzles_completed DESC;


-- ------------------------------------------------------------
-- [Conditie_4] 3) OVERALL ACTIVITY / VOLUME PER STUDENT
-- ------------------------------------------------------------
SELECT
    'Conditie_4'                                  AS condition_label,
    s.username,
    COUNT(e.id)                                AS total_exercises,
    ROUND(AVG(e.is_correct) * 100, 1)          AS accuracy_pct,
    ROUND(AVG(e.response_time), 2)             AS avg_response_time_s,
    COUNT(DISTINCT e.set_id)                   AS sets_played,
    MIN(e.timestamp)                           AS first_seen,
    MAX(e.timestamp)                           AS last_seen,
    TIMESTAMPDIFF(MINUTE, MIN(e.timestamp), MAX(e.timestamp)) AS active_span_minutes
FROM students s
LEFT JOIN exercises e ON e.student_id = s.id
WHERE s.username IN (
        'Ahmed Bouyahyaoui',
        'Alia Mansouri',
        'Amélie Sobrie',
        'Arthur Vanhauwaert',
        'Bilal Tayarsift',
        'Carlo Vetro',
        'Dario Casado',
        'Duke Wandje',
        'Eveleen Kaur',
        'Faith Geurts Mertens',
        'Firass BenameurMoumen',
        'Guillaume Ghistelinck',
        'Ina Gielen',
        'Juna Stoffels',
        'Kelly Martins Barroso',
        'Lee Goossens',
        'Lennert Machiels',
        'Lianne Noelmans',
        'Lucas Somers',
        'Léonié Fieuw',
        'Maya Milissen',
        'Mona El Mannouchi',
        'Remco Dick',
        'Sarah Ouali',
        'Siebe Corstjens',
        'Tijl Van Suetendael'
)
GROUP BY s.id, s.username
ORDER BY total_exercises DESC;


-- ------------------------------------------------------------
-- [Conditie_4] 4) METACOGNITION ENGAGEMENT
-- ------------------------------------------------------------
SELECT
    'Conditie_4'                                             AS condition_label,
    s.username,
    COUNT(CASE WHEN e.meta_self_score IS NOT NULL AND e.meta_self_score > 0 THEN 1 END) AS confidence_answers,
    ROUND(AVG(e.meta_self_score), 2)                      AS avg_confidence,
    ROUND(STDDEV(e.meta_self_score), 2)                   AS sd_confidence,
    ROUND(AVG(e.time_self_score), 2)                      AS avg_time_self_score_s
FROM students s
LEFT JOIN exercises e ON e.student_id = s.id
WHERE s.username IN (
        'Ahmed Bouyahyaoui',
        'Alia Mansouri',
        'Amélie Sobrie',
        'Arthur Vanhauwaert',
        'Bilal Tayarsift',
        'Carlo Vetro',
        'Dario Casado',
        'Duke Wandje',
        'Eveleen Kaur',
        'Faith Geurts Mertens',
        'Firass BenameurMoumen',
        'Guillaume Ghistelinck',
        'Ina Gielen',
        'Juna Stoffels',
        'Kelly Martins Barroso',
        'Lee Goossens',
        'Lennert Machiels',
        'Lianne Noelmans',
        'Lucas Somers',
        'Léonié Fieuw',
        'Maya Milissen',
        'Mona El Mannouchi',
        'Remco Dick',
        'Sarah Ouali',
        'Siebe Corstjens',
        'Tijl Van Suetendael'
)
GROUP BY s.id, s.username
ORDER BY confidence_answers DESC;


-- ------------------------------------------------------------
-- [Conditie_4] 5) GROUP-LEVEL HEADLINE NUMBERS
-- ------------------------------------------------------------
SELECT
    'Conditie_4'                                             AS condition_label,
    COUNT(*)                                              AS n_students,
    ROUND(AVG(unused_coins), 1)                           AS mean_unused_coins,
    ROUND(AVG(spent_coins), 1)                            AS mean_spent_coins,
    ROUND(AVG(pct_spent), 1)                              AS mean_pct_spent,
    SUM(CASE WHEN spent_coins = 0 THEN 1 ELSE 0 END)      AS students_who_spent_nothing,
    SUM(CASE WHEN pct_spent >= 50 THEN 1 ELSE 0 END)      AS students_spent_half_or_more
FROM (
    SELECT
        s.id,
        COALESCE(sp.points, 0)                                AS unused_coins,
        COALESCE(SUM(p.piece_cost), 0)                        AS spent_coins,
        ROUND(
            COALESCE(SUM(p.piece_cost), 0)
            / NULLIF(COALESCE(sp.points,0) + COALESCE(SUM(p.piece_cost),0), 0) * 100,
            1
        ) AS pct_spent
    FROM students s
    LEFT JOIN student_points sp         ON sp.student_id = s.id
    LEFT JOIN student_puzzle_pieces spp ON spp.student_id = s.id
    LEFT JOIN puzzles p                 ON p.id = spp.puzzle_id
    WHERE s.username IN (
        'Ahmed Bouyahyaoui',
        'Alia Mansouri',
        'Amélie Sobrie',
        'Arthur Vanhauwaert',
        'Bilal Tayarsift',
        'Carlo Vetro',
        'Dario Casado',
        'Duke Wandje',
        'Eveleen Kaur',
        'Faith Geurts Mertens',
        'Firass BenameurMoumen',
        'Guillaume Ghistelinck',
        'Ina Gielen',
        'Juna Stoffels',
        'Kelly Martins Barroso',
        'Lee Goossens',
        'Lennert Machiels',
        'Lianne Noelmans',
        'Lucas Somers',
        'Léonié Fieuw',
        'Maya Milissen',
        'Mona El Mannouchi',
        'Remco Dick',
        'Sarah Ouali',
        'Siebe Corstjens',
        'Tijl Van Suetendael'
    )
    GROUP BY s.id, sp.points
) t;
