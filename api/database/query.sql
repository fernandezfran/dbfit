SELECT
    first_merge.doi AS doi,
    first_merge.material AS material,
    first_merge.raw_data_ocv AS isotherm,
    first_merge.raw_data_size AS particle_size,
    second_merge.raw_data_dcoeff AS dcoeff,
    first_merge.function_ocv AS isotherm_function,
    second_merge.function_dcoeff AS dcoeff_function,
    first_merge.input_range_ocv AS isotherm_range,
    second_merge.input_range_dcoeff AS dcoeff_range
FROM (

    SELECT
        d_ocv.material AS material,
        d_ocv.doi AS doi,
        d_ocv.raw_data_ocv,
        d_ocv.function_ocv,
        d_ocv.input_range_ocv,
        d_size.raw_data_size
    FROM (

        SELECT DISTINCT
            parameter.name AS parameter,
            material.name AS material,
            material.class,
            data.raw_data AS raw_data_ocv,
            data.function AS function_ocv,
            data.input_range AS input_range_ocv,
            paper.doi
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name = 'half cell ocv'
        AND class IN ('positive', 'negative')

    ) AS d_ocv
    
    INNER JOIN (

        SELECT DISTINCT
            parameter.name AS parameter,
            material.name AS material,
            material.class,
            data.raw_data AS raw_data_size,
            paper.doi AS doi
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name = 'particle radius'
        AND class IN ('positive', 'negative')

    ) AS d_size

    ON d_ocv.doi = d_size.doi AND d_ocv.material = d_size.material

) AS first_merge

INNER JOIN (

    SELECT DISTINCT
        parameter.name AS parameter,
        material.name AS material,
        material.class,
        data.raw_data AS raw_data_dcoeff,
        data.function AS function_dcoeff,
        data.input_range AS input_range_dcoeff,
        paper.doi
    FROM data
    JOIN paper ON paper.paper_id = data.paper_id
    JOIN material ON material.material_id = data.material_id
    JOIN parameter ON parameter.parameter_id = data.parameter_id
    WHERE parameter.name = 'diffusion coefficient'
    AND class IN ('positive', 'negative')

) AS second_merge

ON first_merge.doi = second_merge.doi
AND first_merge.material = second_merge.material
