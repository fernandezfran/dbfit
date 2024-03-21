SELECT DISTINCT
    parameter.name as parameter,
    material.name as material,
    material.class as class,
    data.raw_data,
    data.raw_data_class,
    parameter.units_output,
    paper.paper_tag,
    paper.doi as doi
FROM data
JOIN paper ON paper.paper_id = data.paper_id
JOIN material ON material.material_id = data.material_id
JOIN parameter ON parameter.parameter_id = data.parameter_id
WHERE parameter.name IN ('diffusion coefficient', 'half cell ocv', 'particle radius')
AND class in ('positive', 'negative')
AND raw_data != 'see function'
