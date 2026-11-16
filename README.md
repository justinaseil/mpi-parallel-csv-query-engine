# MPI CSV GroupBy

Universali MPI sistema SQL tipo užklausoms (WHERE + GROUP BY + agregacija) dideliems CSV failams. Procesas 0 skirsto duomenis 10 000 eilučių blokais, darbininkai filtruoja ir agreguoja, paskirstytojas sujungia rezultatus.

## Naudojimas
```bash
pip install -r requirements.txt
mpirun -n 4 python main_mpi.py --input data.csv \
  --where "Town==Ansonia" --group-by "Property_Type" --agg "Sale_Amount=count"
```
Palaikomi operatoriai: `==, !=, >, <, >=, <=`. SLURM: `sbatch run_mpi.sh`.

## Duomenys
Real Estate Sales 2001–2023 (Data.gov), >1 mln. eilučių. Žr. `data/README.md`.

## Scaling rezultatai
| Procesai | Laikas (s) | Greitėjimas | Efektyvumas |
|---|---|---|---|
| 2 | 2,6145 | 1,00 | 0,5 |
| 4 | 2,1656 | 1,21 | 0,3 |
| 7 | 2,2266 | 1,17 | 0,17 |
