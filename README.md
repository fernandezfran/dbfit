## Repository description

This repository uses the [LiionDB](https://github.com/ndrewwang/liiondb) SQL
database with an extensive catalog of reported battery parameters in scalar,
array, and functional forms. Particle sizes, isotherms, and diffusion 
coefficients are extracted from this database using an SQL query to merge these
parameters when they come from the same work. Data cleaning is performed to
obtain these parameters in the required form to fit with a previously developed
heuristic model. All this is done using the 
[galpynostatic](https://github.com/fernandezfran/galpynostatic) package along
with other Python libraries of the data science stack.
