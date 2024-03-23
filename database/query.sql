SELECT
    first_merge.doi_ocv AS doi,
    first_merge.material_ocv AS material,
    first_merge.raw_data_ocv AS isotherm,
    first_merge.raw_data_size AS particle_size,
    second_merge.raw_data_dcoeff AS dcoeff,
    first_merge.function_ocv AS isotherm_function,
    second_merge.function_dcoeff AS dcoeff_function,
    first_merge.input_range_ocv AS isotherm_range,
    second_merge.input_range_dcoeff AS dcoeff_range
FROM (

    SELECT d_ocv.*, d_size.*
    FROM (

        SELECT DISTINCT
            parameter.name AS parameter_ocv,
            material.name AS material_ocv,
            material.class AS class_ocv,
            data.raw_data AS raw_data_ocv,
            data.raw_data_class AS raw_data_class_ocv,
            data.function AS function_ocv,
            data.input_range AS input_range_ocv,
            parameter.units_output AS units_output_ocv,
            paper.paper_tag,
            paper.doi AS doi_ocv
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name IN ('diffusion coefficient', 'half cell ocv', 'particle radius')
        AND class IN ('positive', 'negative')

    ) AS d_ocv
    
    INNER JOIN (

        SELECT DISTINCT
            parameter.name AS parameter_size,
            material.name AS material_size,
            material.class AS class_size,
            data.raw_data AS raw_data_size,
            data.raw_data_class AS raw_data_class_size,
            data.function AS function_size,
            parameter.units_output AS units_output_size,
            paper.paper_tag,
            paper.doi AS doi_size
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name IN ('diffusion coefficient', 'half cell ocv', 'particle radius')
        AND class IN ('positive', 'negative')

    ) AS d_size

    ON d_ocv.doi_ocv = d_size.doi_size AND d_ocv.material_ocv = d_size.material_size
    AND d_ocv.parameter_ocv != d_size.parameter_size

) AS first_merge

INNER JOIN (

    SELECT DISTINCT
        parameter.name AS parameter_dcoeff,
        material.name AS material_dcoeff,
        material.class AS class_dcoeff,
        data.raw_data AS raw_data_dcoeff,
        data.raw_data_class AS raw_data_class_dcoeff,
        data.function AS function_dcoeff,
        data.input_range AS input_range_dcoeff,
        parameter.units_output AS units_output_dcoeff,
        paper.paper_tag,
        paper.doi AS doi_dcoeff
    FROM data
    JOIN paper ON paper.paper_id = data.paper_id
    JOIN material ON material.material_id = data.material_id
    JOIN parameter ON parameter.parameter_id = data.parameter_id
    WHERE parameter.name IN ('diffusion coefficient', 'half cell ocv', 'particle radius')
    AND class IN ('positive', 'negative')

) AS second_merge

ON first_merge.doi_ocv = second_merge.doi_dcoeff 
AND first_merge.material_ocv = second_merge.material_dcoeff
AND first_merge.parameter_ocv != second_merge.parameter_dcoeff
AND first_merge.parameter_size != second_merge.parameter_dcoeff
WHERE first_merge.parameter_ocv = 'half cell ocv'
AND first_merge.parameter_size = 'particle radius';
